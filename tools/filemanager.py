import os, glob


class FileManager:
    def __init__(self):
        self.create_dirs()
        self.clean_dirs()

    def del_files(self, path: str, ext: str) -> None:
        """
        Deletes all files with specified extention at specified folder path

        Parameters:
        path:str, required
            Folder path.
        ext:str, required
            File extension. "*" for all files.

        Returns:
        None
        """
        res_files = False
        loc = os.path.join(path, ext)
        files = glob.glob(loc)
        if len(files) > 0:
            res_files = True
            print("Found {} file(s). Deleting...".format(len(files)))
            for f in files:
                os.remove(f)
        elif len(files) == 0:
            print("No files found")

        return res_files

    def create_dirs(self) -> None:
        """
        Creates all required directories

        Parameters:
        None

        Returns:
        None
        """
        dirs_exist = False
        dir_dict = {
            "sd_flood": "output/flood",
            "sd_preflood": "output/preflood",
            "sd_flood_extents": "output/flood_extents",
            "sd_maxflood": "output/maxflood",
            "sd_csv": "output/csv",
            "sd_plots": "output/plots",
            "sd_shape": "output/shape",
            "sd_input": "input",
        }

        for k in dir_dict:
            if not os.path.exists(dir_dict[k]):
                os.makedirs(dir_dict[k])
            else:
                dirs_exist = True

        if dirs_exist:
            print("All directories exist")
        else:
            print("All directories created")

    def clean_dirs(self) -> None:
        """
        Creates directories if they dont exist or deletes residual files if they exist.

        Parameters:
        None

        Returns:
        None
        """
        dir_dict = {
            "sd_flood": "output/flood",
            "sd_preflood": "output/preflood",
            "sd_flood_extents": "output/flood_extents",
            "sd_maxflood": "output/maxflood",
        }

        for k in dir_dict:
            if not os.path.exists(dir_dict[k]):
                os.makedirs(dir_dict[k])
            else:
                dirs_exist = True
                r = self.del_files(dir_dict[k], "*")

        if not r:
            print("No residual files to delete.")
