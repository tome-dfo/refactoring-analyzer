# Refactoring analyzer

Tool for analyzing which python files are most suited for refactoring effort. 
The tool finds all python files in a directory or its subdirectories and calculates file complexity, using cyclic complexity by default. It then analyzes git file changes and combines the data to create a Eisenhower matrix with a proposed prioritization of files.

## Dependencies

Dependencies are listed here, but can be installed from the requirements.txt file.

 - radon
    - colorama
    - mando
    - six
 - GitPython
    - smmap
    - gitdb