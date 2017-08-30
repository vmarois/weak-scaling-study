#include <dolfin.h>
#include "Poisson.h"

using namespace dolfin;

// Source term (right-hand side)
class Source : public Expression
{
  public:
  Source(double xmax, double ymax) : _xmax(xmax), _ymax(ymax)
  {}

  void eval(Array<double>& values, const Array<double>& x) const
  {
    double dx = x[0]/_xmax - 0.5;
    double dy = x[1]/_ymax - 0.5;
    values[0] = 10*exp(-(dx*dx + dy*dy)/0.02);
  }

  double _xmax, _ymax;
};

// Normal derivative (Neumann boundary condition)
class dUdN : public Expression
{
  public:
  dUdN(double xmax): _xmax(xmax)
  {}

  void eval(Array<double>& values, const Array<double>& x) const
  { values[0] = sin(5*x[0]/_xmax); }

  double _xmax;
};

// Sub domain for Dirichlet boundary condition
class DirichletBoundary : public SubDomain
{
  public:
  DirichletBoundary(double xmax): _xmax(xmax)
  {}

  bool inside(const Array<double>& x, bool on_boundary) const
  { return x[0] < DOLFIN_EPS or x[0] > _xmax - DOLFIN_EPS; }

  double _xmax;
};

// Calculate number of vertices for any given level of refinement
std::int64_t nvertices(int i, int j, int k, int nrefine)
{
  std::int64_t nv = (i + 1)*(j + 1)*(k + 1);
  std::int64_t earr[3] = {1, 3, 7};
  for (int r = 0; r < nrefine; ++r)
  {
    std::size_t ne
      = earr[0]*(i + j + k) + earr[1]*(i*j + j*k + k*i) + earr[2]*i*j*k;
    nv += ne;
    earr[0] *= 2;
    earr[1] *= 4;
    earr[2] *= 8;
  }
  return nv;
}


int main(int argc, char *argv[])
{
  parameters.parse(argc, argv);

  Parameters application_parameters("application_parameters");
  application_parameters.add("pc", "hypre_amg");
  application_parameters.add("solver", "cg");
  application_parameters.add("ndofs", 640000);
  application_parameters.add("output", "vtk");
  application_parameters.add("output_dir", ".");
  application_parameters.add("dim", 3);
  application_parameters.add("xmlname", "");
  application_parameters.parse(argc, argv);
  const std::string preconditioner = application_parameters["pc"];
  const std::string solver_type = application_parameters["solver"];
  const std::string output = application_parameters["output"];
  const std::string output_dir = application_parameters["output_dir"];
  const std::size_t ndofs = application_parameters["ndofs"];
  const std::size_t dim = application_parameters["dim"];
  const std::string xmlname = application_parameters["xmlname"];

  parameters["mesh_partitioner"] = "ParMETIS";

  Timer t7("ZZZ Total");
  Timer t0("ZZZ Create Mesh");

  // Get number of processes
  const std::size_t ncores = MPI::size(MPI_COMM_WORLD);
  std::int64_t N = (ndofs*ncores);

  std::size_t Nx, Ny, Nz;
  int r = 0;

  if (dim == 3)
  {
    // Get initial guess for Nx, Ny, Nz, r
    Nx = 1;
    std::int64_t nc = 0;
    while(nc < N)
    {
      nc = nvertices(Nx, Nx, Nx, r);
      ++Nx;
      if (Nx > 100)
      {
        Nx = 1;
        ++r;
      }
    }

    Ny = Nx;
    Nz = Nx;

    std::size_t i0 = Nx - 10;
    std::size_t mindiff = 1000000;
    for (std::size_t i = i0; i < i0 + 20; ++i)
      for (std::size_t j = i - 5; j < i + 5; ++j)
        for (std::size_t k = i - 5; k < i + 5; ++k)
        {
          std::size_t diff = std::abs(nvertices(i, j, k, r) - N);
          if (diff < mindiff)
          {
            mindiff = diff;
            Nx = i;
            Ny = j;
            Nz = k;
          }
        }
  }
  else if (dim == 2)
  {
    Nz = 1;
    Nx = 1;
    std::int64_t nc = 0;
    while(nc < N)
    {
      nc = nvertices(Nx, Nx, Nz, r);
      ++Nx;
      if (Nx > 200)
      {
        Nx = 1;
        ++r;
      }
    }

    Ny = Nx;

    std::size_t i0 = Nx - 10;
    std::size_t mindiff = 1000000;
    for (std::size_t i = i0; i < i0 + 20; ++i)
      for (std::size_t j = i - 5; j < i + 5; ++j)
      {
        std::size_t diff = std::abs(nvertices(i, j, Nz, r) - N);
        if (diff < mindiff)
        {
          mindiff = diff;
          Nx = i;
          Ny = j;
        }
      }
  }
  else if (dim == 1)
  {
    Nz = 1;
    Ny = 1;
    Nx = 1;
    std::int64_t nc = 0;
    while(nc < N)
    {
      nc = nvertices(Nx, Ny, Nz, r);
      ++Nx;
      if (Nx > 10000)
      {
        Nx = 1;
        ++r;
      }
    }

    std::size_t i0 = Nx - 2;
    std::size_t mindiff = 1000000;
    for (std::size_t i = i0; i < i0 + 4; ++i)
    {
      std::size_t diff = std::abs(nvertices(i, Ny, Nz, r) - N);
      if (diff < mindiff)
      {
        mindiff = diff;
        Nx = i;
      }
    }


  }
  else
  {
    dolfin_error("main.cpp", "set dimension", "dim must be 1, 2 or 3");
  }

  double xmax = (double)Nx;
  double ymax = (double)Ny;
  double zmax = (double)Nz;

  std::shared_ptr<const Mesh> mesh(new BoxMesh(Point(0.0, 0.0, 0.0),
                                               Point(xmax, ymax, zmax),
                                               Nx, Ny, Nz));

  if (MPI::rank(mesh->mpi_comm())==0)
  {
    std::cout << "UnitCube (" << Nx << "x" << Ny << "x" << Nz
              << ") to be refined " <<  r <<  " times\n";
  }

  for (unsigned int i = 0; i != r; ++i)
    mesh = std::make_shared<Mesh>(refine(*mesh, false));

  t0.stop();
  Timer t1("ZZZ FunctionSpace");

  auto V = std::make_shared<Poisson::FunctionSpace>(mesh);

  if (MPI::rank(mesh->mpi_comm()) == 0)
  {
    std::cout << "SolverType: " << solver_type << "\n";
    std::cout << "PreConditioner: " << preconditioner << "\n";
    std::cout << "Box: " << Nx << " " << Ny << " " << Nz << "\n";
    std::cout << "Cores: " << ncores << "\n";
    std::cout << "Degrees of freedom:          " <<  V->dim() << "\n";
    std::cout << "Degrees of freedom per core: "
              <<  V->dim()/MPI::size(mesh->mpi_comm()) << "\n";
  }

  t1.stop();
  Timer t2("ZZZ DirichletBC");

  // Define boundary condition
  auto u0 = std::make_shared<Constant>(0.0);
  auto boundary = std::make_shared<DirichletBoundary>(xmax);
  auto bc = std::make_shared<DirichletBC>(V, u0, boundary);

  // Define variational forms
  auto a = std::make_shared<Poisson::BilinearForm>(V, V);
  auto L = std::make_shared<Poisson::LinearForm>(V);

  // Attach coefficients
  auto f = std::make_shared<Source>(xmax, ymax);
  auto g = std::make_shared<dUdN>(xmax);
  L->f = f;
  L->g = g;

  t2.stop();
  Timer t3("ZZZ PETSC options");

  if (preconditioner == "petsc_amg")
  {
    //    PETScOptions::set("pc_gamg_sym_graph", true);
    PETScOptions::set("pc_gamg_coarse_eq_limit", 500);
    PETScOptions::set("mg_levels_esteig_ksp_type", "cg");
    PETScOptions::set("mg_levels_ksp_type", "chebyshev");
    PETScOptions::set("mg_levels_pc_type", "jacobi");
    PETScOptions::set("mg_levels_ksp_chebyshev_esteig_steps", 50);
    PETScOptions::set("mg_levels_esteig_ksp_max_it", 50);
    PETScOptions::set("mg_levels_ksp_chebyshev_esteig_random");
    //PETScOptions::set("mg_coarse_ksp_type", "preonly");
    //PETScOptions::set("mg_coarse_pc_type", "lu");
    //PETScOptions::set("mg_coarse_pc_factor_mat_solver_package",
    //                  "superlu_dist");

    // Smoothed aggregation
    PETScOptions::set("pc_gamg_type", "agg");
    PETScOptions::set("pc_gamg_nsmooths", 1);
    PETScOptions::set("options_left");

  }
  else if (preconditioner == "hypre_amg")
  {
    // Number of levels of aggresive coarsening for BoomerAMG (note:
    // increasing this appear to lead to substantial memory savings)
    PETScOptions::set("pc_hypre_boomeramg_agg_nl", 4);
    PETScOptions::set("pc_hypre_boomeramg_agg_num_paths", 2);

    // Truncation factor for interpolation (note: increasing towards 1
    // appears to reduce memory usage)
    PETScOptions::set("pc_hypre_boomeramg_truncfactor", 0.9);

    // Max elements per row for interpolation operator
    PETScOptions::set("pc_hypre_boomeramg_P_max", 5);

    // Strong threshold (BoomerAMG docs recommend 0.5 - 0.6 for 3D
    // Poisson)
    PETScOptions::set("pc_hypre_boomeramg_strong_threshold", 0.5);
  }
  else if (preconditioner == "ml_amg")
  {
    // Try some options to make the smoothing more reliable for ML
    PETScOptions::set("mg_levels_ksp_chebyshev_estimate_eigenvalues", "0.0,0.5,0.0,4.2");
    PETScOptions::set("mg_levels_est_ksp_type", "cg");
    PETScOptions::set("mg_levels_est_ksp_max_it", 70);
  }

  PETScOptions::set("ksp_view");

  t3.stop();
  Timer t4("ZZZ Assemble");

  // Compute solution
  Function u(V);

  // Create assembler
  SystemAssembler assembler(a, L, {bc});

  // Assemble system
  std::shared_ptr<GenericMatrix> A(new PETScMatrix);
  std::shared_ptr<GenericVector> b(new PETScVector);
  assembler.assemble(*A, *b);

  // Create solver
  PETScKrylovSolver solver(solver_type, preconditioner);
  solver.set_from_options();
  solver.parameters["relative_tolerance"] = 1.0e-10;
  solver.parameters["monitor_convergence"] = true;
  solver.set_operator(A);
  if (MPI::rank(mesh->mpi_comm()) == 0)
    info(solver.parameters, true);

  t4.stop();
  Timer t5("ZZZ Solve");

  // Solve
  solver.solve(*u.vector(), *b);

  t5.stop();
  Timer t6("ZZZ Output");

  if (output == "vtk")
  {
    //  Save solution in VTK format
    std::string filename = output_dir + "/output/others/poisson-"
      + std::to_string(ncores) + ".pvd";
    File file(filename);
    file << u;
  }
  else if (output == "xdmf")
  {
    //  Save solution in XDMF format
    std::string filename = output_dir + "/output/others/poisson-"
      + std::to_string(ncores) + ".xdmf";
    XDMFFile file(filename);
    file.write(u);
  }
  
  t6.stop();
  t7.stop();

  std::string filename = output_dir + "/output/timings/timings_" + xmlname + ".xml";

  //Save timings to an XML file
  if (MPI::rank(mesh->mpi_comm()) == 0)
  	{File file(MPI_COMM_SELF, filename);
     	Table t = timings(TimingClear::clear, {TimingType::wall});
    	file << t;}

  //Save ndofs per core & total to an xml file
  std::string dofs_filename = output_dir + "/output/dofs/dofs_" + xmlname + ".xml";
  
  if(MPI::rank(mesh->mpi_comm()) == 0)
  	{File dofsfile(MPI_COMM_SELF, dofs_filename);
  	 Table dofsvalue("weak-scaling-dofs");
	 dofsvalue.set("Total", "ndofs", (V->dim()));
         dofsvalue.set("Total", "reps", 1);
	 dofsvalue.set("Per core", "ndofs", (V->dim()/MPI::size(mesh->mpi_comm())));
	 dofsvalue.set("Per core", "reps", 1);
  	 dofsfile << dofsvalue;}

  std::string filename2 = output_dir + "/output/partitions/partitions.xdmf";
  XDMFFile file2(filename2);
  CellFunction<std::size_t> partitioning(mesh, dolfin::MPI::rank(mesh->mpi_comm()));
  file2.write(partitioning);

  list_timings(TimingClear::clear, {TimingType::wall});

  return 0;
}
