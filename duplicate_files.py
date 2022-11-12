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

    def get_hash(self) -> hash:
        """returns file's md5-hash value in hex-digit format"""
        with open(self.path, "rb") as file:
            self.hash = md5(file.read()).hexdigest()


class DuplicateFileHandler:

    def __init__(self):
        self.files_list: list = []
        self.sort_option: bool = True
        self.result_dict: dict = {}

    def get_files_list(self, extension=None):
        """recursively scans directory provided and creates the list of absolute paths filtering by extension"""
        abs_paths_lst = [
            join(root, name)
            for root, dirs, files in os.walk(args.d, topdown=True)
            for name in files
            if not extension or name.endswith(extension)
        ]

        self.files_list = [File(size=getsize(path), path=path) for path in abs_paths_lst]

    def check_for_duplicates(self):
        check = input("\nCheck for duplicates? (Y/N): ").lower()

        if check == "y":
            files_size_list = sorted((file.size for file in self.files_list), reverse=self.sort_option)
            sizes_with_several_files = [file.size for file in self.files_list if files_size_list.count(file.size) > 1]
            self.files_list = [file for file in self.files_list if file.size in sizes_with_several_files]

            # calculate hashes
            for file in self.files_list:
                file.get_hash()
        elif check == "n":
            exit(print("OK. Bye!"))

        else:
            print(OPTION_ERROR)
            return self.check_for_duplicates()

    def print_duplicate_files(self):
        """this function prints the output(result) of the program. if a format key: \n values"""
        del_dict = {}
        hashes = [file.hash for file in self.files_list]
        duplicate_hashes = [file.hash for file in self.files_list if hashes.count(file.hash) > 1]
        self.files_list = filter(lambda x: x.hash in duplicate_hashes, self.files_list)

        self.result_dict = {}
        for f in self.files_list:
            if f.size not in self.result_dict:
                self.result_dict[f.size] = {f.hash: [f.path]}
            else:
                if f.hash not in self.result_dict[f.size]:
                    self.result_dict[f.size].update({f.hash: [f.path]})
                else:
                    if f.path not in self.result_dict[f.size][f.hash]:
                        self.result_dict[f.size][f.hash].append(f.path)



        size_hash_dictionary = dict(sorted(self.result_dict.items(), reverse=self.sort_option))

        i = 1
        for file_size, file_hashes in size_hash_dictionary.items():
            if file_hashes:
                print()
                print(file_size, "bytes\n")
                for file_hash in file_hashes:
                    print("Hash:", file_hash)
                    for file_path in file_hashes[file_hash]:
                        print(i, file_path)
                        del_dict[i] = file_path
                        i += 1
        print()
        if del_dict:
            return self.delete_files(del_dict)
        else:
            exit(print(f"{Fore.GREEN}No duplicates found!"))

    def delete_files(self, dl_dict) -> int:
        decision = input("Delete files? (Y/N): ")
        if decision.lower() not in {"y", "n"}:
            print(OPTION_ERROR)
            return self.delete_files(dl_dict)

        if decision.lower() == "y":
            while True:
                file_numbers = input("Enter file numbers to delete separated by space:\n").split(" ")
                try:
                    file_numbers = sorted([int(number) for number in file_numbers], reverse=True)
                    if file_numbers[0] not in dl_dict.keys():
                        raise ValueError
                except ValueError:
                    print(OPTION_ERROR)
                else:
                    freed_space = 0
                    for number in file_numbers:
                        freed_space += getsize(dl_dict[number])
                        os.remove(dl_dict[number])
                    print(f"{Fore.GREEN}Total freed up space: {freed_space} bytes")
                    break

    def start(self):
        """this is the main function which calls other functions in a defined order"""
        self.get_files_list(input("Enter the file format or press 'return' for all: "))
        self.check_for_duplicates()
        self.print_duplicate_files()


def fatal_error(msg):
    exit(print(f"{Fore.RED}{msg}"))

if __name__ == "__main__":
    parser = ArgumentParser(description="This program finds duplicate files in a given folder and sub-folders.")
    parser.add_argument('-d', type=str, default=os.getcwd(), required=False, help='provide directory')
    parser.add_argument('-s', type=str, default='desc', required=False, help="'asc' or 'desc'")
    args = parser.parse_args()

    if not isinstance(args.d, str) or not os.path.exists(args.d):
        fatal_error('Incorrect path provided.')

    if not isinstance(args.s, str) or args.s not in ('asc', 'desc'):
        fatal_error('Incorrect sort option.')

    handler = DuplicateFileHandler()
    handler.start()
