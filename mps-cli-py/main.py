# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


from pathlib import Path

from model.builder.SLanguageBuilder import SLanguageBuilder
from model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder

def print_paths(str_path):
    print("in print " + str_path)
    asm_paths = []
    for pth in Path(str_path).rglob('*.msd'):
        asm_paths.append(pth)
    for p in asm_paths:
        print(p)

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Strg+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    builder = SSolutionsRepositoryBuilder()
    repo = builder.build('c:\\work\\mps-cli\\mps_test_projects\\mps_cli_lanuse_file_per_root')
    for sol in repo.solutions:
        print(sol.name, sol.uuid)

    for lan_name in SLanguageBuilder.languages.keys():
        lan = SLanguageBuilder.languages[lan_name]
        print(lan.name, lan.uuid)
        for conc in lan.concepts:
            print("\t", conc.name)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
