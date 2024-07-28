import sys
sys.path.insert(1, '..')

from model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder

builder = SSolutionsRepositoryBuilder()
repo = builder.build('..\\..\\mps_test_projects\\mps_cli_lanuse_file_per_root')