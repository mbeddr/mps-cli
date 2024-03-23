const MPSR_TOP_MODEL_PATH: &'static str = "/models/mps.cli.lanuse.library_top.library_top";
const MPSR_SOLUTION_MPS_CLI_LANUSE_LIBRARY_TOP_: &'static str = "/solutions/mps.cli.lanuse.library_top";
const MPSR_FILE_PATH: &'static str = "/munich_library.mpsr";
const PATH_TO_MPS_TEST_PROJECTS: &'static str = "../mps_test_projects";
const PATH_TO_FILE_PER_ROOT_PROJECT: &'static str = "/mps_cli_lanuse_file_per_root";
const MPSR_MODEL_FILE_NAME: &'static str = "/.model";
const MPS_CLI_LANUSE_LIBRARY_TOP_MSD: &'static str = "/mps.cli.lanuse.library_top.msd";

fn get_path_to_test_projects() -> String {
    String::from(PATH_TO_MPS_TEST_PROJECTS)
}


pub fn get_path_to_mps_cli_lanuse_file_per_root() -> String {
    get_path_to_test_projects() + PATH_TO_FILE_PER_ROOT_PROJECT
}

fn get_path_to_mpsr_solution() -> String {
    get_path_to_mps_cli_lanuse_file_per_root() + MPSR_SOLUTION_MPS_CLI_LANUSE_LIBRARY_TOP_
}

pub fn get_path_to_mpsr_example_lib_file() -> String {
    get_path_to_example_mpsr_model_files() + MPSR_FILE_PATH
}

pub fn get_path_to_example_mpsr_model_files() -> String {
    get_path_to_mpsr_solution() + MPSR_TOP_MODEL_PATH
}

pub fn get_path_to_model_mpsr_example_lib_file() -> String {
    get_path_to_mpsr_solution() + MPSR_TOP_MODEL_PATH + MPSR_MODEL_FILE_NAME
}

pub fn get_path_to_mps_cli_lanuse_library_top_msd_file() -> String {
    get_path_to_mpsr_solution() + MPS_CLI_LANUSE_LIBRARY_TOP_MSD
}