#!/usr/bin/env python3
import os
from hashlib import md5
from os.path import getsize, join
from argparse import ArgumentParser
from colorama import init, Fore
init(autoreset=True)

OPTION_ERROR = f"{Fore.RED}Wrong option"


class File:

    def __init__(self, path, size):
        self.size = size
        self.path = path
        self.hash = None

    def compute_md5_hash(self) -> hash:
        """returns file's md5-hash value in hex-digit format"""
        with open(self.path, "rb") as file:
            self.hash = md5(file.read()).hexdigest()


class DuplicateFileHandler:

    def __init__(self):
        self.files_tuple = None
        self.sort_option: bool = SORT
        self.file_extension: str = args.extension

    def get_duplicate_files(self):
        """recursively scans directory provided and creates a tuple of absolute paths filtering by extension"""
        # 
        abs_paths_tuple = tuple(
            join(root, name)
            for root, dirs, files in os.walk(args.directory, topdown=True)
            for name in files
            if not self.file_extension or name.endswith(self.file_extension)
        )

        file_sizes = tuple(getsize(path) for path in abs_paths_tuple)
        self.files_tuple = tuple(
            File(size=getsize(path), path=path) for path in abs_paths_tuple if file_sizes.count(getsize(path)) > 1
        )

        # calculating hashes only for potential duplicates
        for file in self.files_tuple:
            file.compute_md5_hash()

        # removing objects with unique hash from the list as those are definitely not a duplicate!
        file_hashes = tuple(file.hash for file in self.files_tuple)
        self.files_tuple = tuple(filter(lambda x: file_hashes.count(x.hash) > 1, self.files_tuple))
        # sort for correct final print 
        self.files_tuple = tuple(
            sorted(self.files_tuple, key=lambda f: (f.size, f.hash), reverse=self.sort_option)
        )

    def print_duplicate_files(self):
        """this function prints the output(result) of the program. if a format key: \n values"""
        del_dict = {}
        file_size = file_hash = None
        for i, file in enumerate(self.files_tuple, start=1):
            # making sure size is printed only once
            if file_size != file.size:
                file_size = file.size
                print(f"\n{file_size:_} bytes\n")
            if file_hash != file.hash:
                file_hash = file.hash
                print("Hash:", file_hash)

            print(f"{i}.", file.path)
            del_dict[i] = file
            i += 1
        print()
        if del_dict:
            return DuplicateFileHandler.delete_files(del_dict)
        else:
            msg = "No duplicates found"
            exit(
                print(
                    f"{Fore.GREEN}{msg}!"
                    if not self.file_extension
                    else f"{Fore.GREEN}{msg} with file extension {Fore.RED}{self.file_extension} {Fore.GREEN}!"
                )
            )

    @staticmethod
    def delete_files(dl_dict):
        decision = input("Delete files? (Y/N): ")
        while decision.lower() not in {"y", "n"}:
            print(OPTION_ERROR)
            return DuplicateFileHandler.delete_files(dl_dict)

        if decision.lower() == "y":
            while True:
                file_numbers = input("Enter file numbers to delete separated by space:\n").split(" ")
                try:
                    file_numbers = sorted([int(number) for number in file_numbers], reverse=True)
                    # checking the biggest index if it exists - all other too!
                    if file_numbers[0] not in dl_dict.keys():
                        raise ValueError
                except ValueError:
                    print(OPTION_ERROR)
                else:
                    freed_space = 0
                    for number in file_numbers:
                        freed_space += dl_dict[number].size
                        os.remove(dl_dict[number].path)
                    print(f"{Fore.GREEN}Total freed up space: {freed_space:_} bytes")
                    break

    def start(self):
        """this is the main function which calls other functions in a defined order"""
        self.get_duplicate_files()
        self.print_duplicate_files()


def _fatal_error(msg):
    exit(print(f"{Fore.RED}{msg}"))


if __name__ == "__main__":
    parser = ArgumentParser(description="This program finds duplicate files in a given folder and sub-folders.")
    parser.add_argument('-d', '--directory', type=str, default=os.getcwd(), required=False, help='provide directory')
    parser.add_argument('-e', '--extension', type=str, default=None, required=False, help='provide file extension')
    parser.add_argument('-s', '--sort', type=str, default='desc', required=False, help="'asc' or 'desc'")
    args = parser.parse_args()

    # validate args
    if not isinstance(args.directory, str) or not os.path.exists(args.directory):
        _fatal_error('Incorrect path provided.')

    if not isinstance(args.sort, str) or args.sort not in ('asc', 'desc'):
        _fatal_error('Incorrect sort option.')
    SORT = False if args.sort == 'asc' else True

    handler = DuplicateFileHandler()
    handler.start()
