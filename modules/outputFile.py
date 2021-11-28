import os

def outputFile(outputFile, outputRaster):
    
    outputFile_FolderLoc = os.path.dirname(outputCSV_Loc)
    if not os.path.exists(outputFile_FolderLoc):
        os.makedirs(outputFile_FolderLoc)
        
    gs.run_command('r.out.gdal',
                   input=outputRaster,
                   output=outputFile,
                   overwrite=True)
    gs.run_command('r.out.png',
                   input=outputRaster,
                   output=outputFile,
                   overwrite=True)
