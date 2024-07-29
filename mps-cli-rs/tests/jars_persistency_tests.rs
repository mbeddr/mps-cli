mod model_completeness_tests;
use mps_cli::build_repo_from_directory;

#[test]
fn test_build_repository() {
    let path = "../mps_test_projects/mps_cli_lanuse_binary/"; 
    let repo = build_repo_from_directory(path.to_string()); 
    model_completeness_tests::check_model_completeness(&repo, "mps.cli.lanuse.library_top", "mps.cli.lanuse.library_second");
}