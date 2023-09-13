import argparse
import sqlite3
import sys
import os
from dataclasses import dataclass
import radon.complexity as radon
import git
import pandas as pd
import matplotlib.pyplot as plt

@dataclass
class FileComplexity:
    filename: str
    fullpath: str
    blocks: list
    file_avg_complexity: int
    file_changes: int

@dataclass
class Block:
    type: str
    name: str
    cc_score: int
    rank: str

def parse_arguments():
    """
    Parses command-line arguments.
    """

    parser = argparse.ArgumentParser(description='Process command-line arguments')

    parser.add_argument('path',
                        type=str,
                        help='path to folder')
    
    try: 
        if not len(sys.argv) > 1:
            print('''
                    Refactoring Analyzer
                    
                    This app helps propose which python files are in most need of refactoring
                  
                    Arguments: path to root folder
                    ''')
            sys.exit(0)
        args = parser.parse_args()

        if not os.path.isdir(args.path):
            raise Exception(f"{args.path} is not a directory")
        
    except Exception as e:
        print(f'An error occured while parsing the arguments: {e}')
        sys.exit(1)

    return args

def find_files(path): 
    files_found = []   
    for root, dirs, x in os.walk(path):
        for file in x:
            if file.endswith(".py"):
                files_found.append(FileComplexity(
                    filename=file,
                    fullpath=os.path.join(root, file),
                    blocks=[],
                    file_avg_complexity=-1,
                    file_changes=-1
                ))
    print(f'Found {len(files_found)} files')
    return files_found

def calculate_complexity(files):
    for f in files:
        code_blocks = []
        sum_complexity = 0
        with open(f.fullpath,'r', errors='ignore') as file_obj:
            cc = radon.cc_visit(file_obj.read())
            for block in cc:
                print(block)
                code_blocks.append(Block(
                    type=type(block).__name__,
                    name=block.name,
                    cc_score=block.complexity,
                    rank=rank_by_score(block.complexity)
                ))
                sum_complexity+=block.complexity
        f.blocks = code_blocks
        if sum_complexity > 0 and len(code_blocks) > 0:
            f.file_avg_complexity = sum_complexity/len(code_blocks)
        else:
            f.file_avg_complexity = 0
    return files

def rank_by_score(score):
    ''' CC score	Rank	Risk
        1 - 5	    A	    low - simple block
        6 - 10	    B	    low - well structured and stable block
        11 - 20	    C	    moderate - slightly complex block
        21 - 30	    D	    more than moderate - more complex block
        31 - 40	    E	    high - complex block, alarming
        41+	        F	    very high - error-prone, unstable block'''
    if 1 <= score <= 5:
        return 'A'
    elif 6 <= score <= 10:
        return 'B'
    elif 11 <= score <= 20:
        return 'C'
    elif 21 <= score <= 30:
        return 'D'
    elif 31 <= score <= 40:
        return 'E'
    elif score >= 41:
        return 'F'

def count_filechanges(files, repo_path):
    repo = git.Repo(repo_path)
    for f in files:
        file_commits_generator = repo.iter_commits(all=True, max_count=1000, paths=f.fullpath)
        commits_for_file = [c for c in file_commits_generator]
        f.file_changes=len(commits_for_file)

def print_results(result):
    for r in result:
        print(f'|-> {r.filename}')
        print(f'   - Average Cyclomatic Complexity: {r.file_avg_complexity} (Rank {rank_by_score(r.file_avg_complexity)})')
        print(f'   - Number of commits: {r.file_changes}')
        print(f'   Code Blocks:')
        for b in r.blocks:
            print(f'   |-> {b.type} {b.name}: {b.rank} ({b.cc_score})')

def eisenhower_grouping(data):
    

if __name__=="__main__":
    args = parse_arguments()
    files = find_files(args.path)
    complexity_result = calculate_complexity(files)
    filechange_result = count_filechanges(complexity_result, args.path)
    print_results(complexity_result)
        
    