import os
import json
import glob


class BaseView:
    """
    Class defining details and properties common to all views.

    Parameters
    ----------
    request : :class:`pyramid.Request`
        The request object coming into the view.
    """

    def __init__(self, request):
        self.request = request

    @property
    def dependencies(self):
        """
        Accessible as a property of an IndexView object.

        All of the client dependencies defined by clientdependencies.json
        so that the index can load the js and css files relating to those
        dependencies (example dependencies would be angular.js, jquery,
        twitter bootstrap, etc.)

        clientdependencies.json should be organized as follows:
        {
            "<dependency>": {
                "version": "<version>",
                ["css": <array of css files to load>,]
                ["js": <array of js files to load>]
            }
        },
        ...

        where <dependency> and <version> is the name and version of the package
        as known by bower (setup.py also uses clientdependencies.json to
        download and install these packages using bower), and where "css" and
        "js" are optional parameters specifying arrays of filepaths, relative
        to public/lib/<dependency>/ of the cs and js files to load into the
        index view.

        Returns
        -------
        clientdependencies : dictionary
            The json from clientdependencies.json described above parsed
            into a python dictionary.
        """
        with open('dependency_autoload.json', 'r') as f:
            return json.load(f).items()

    @property
    def stylesheets(self):
        """
        Accessible as a property of an View object.

        The filepaths of all css files in the static_path `tdf:public/css`
        (relative to the static_path). See :meth:`walk_paths`.

        Returns
        -------
        paths : list
            The relative paths to all css files described above.
        """
        static_path = self.request.static_path('tdf:public/css')
        return BaseView.walk_paths(static_path, '%s/tdf%s/*')

    @property
    def scripts(self):
        """
        Accessible as a property of an View object.

        The filepaths of all js files in the static_path `tdf:public/js`
        (relative to the static_path). See :meth:`walk_paths`.

        Returns
        -------
        paths : list
            The relative paths to all js files described above.
        """
        static_path = self.request.static_path('tdf:public/js')
        return BaseView.walk_paths(static_path, '%s/tdf%s/*')

    @staticmethod
    def walk_paths(static_path, fmt):
        """
        Recursively walks and finds all paths relative to the combination of
        `static_path` and `fmt`.

        Parameters
        ----------
        static_path : str (filepath)
            A static path defined by the TDF system. One example of a static
            path is: `request.static_path('tdf:public/css')`.
        fmt : str
            A string with two format replacements %s. This is used to create a
            full path to the system. The first %s is replaced with the current
            working directory, and teh second is replaced by the static path.
            For example, if the directory that needs to be walked is
            `/home/user/pytdf/tdf/public/css/`, where `/home/user/pytdf` is the
            current working directory and `/public/css` is the static path,
            then the format code given should be `%s/tdf%s/*` indicating that
            all files and subdirectories in the desired folder should be
            walked.

        Returns
        -------
        files : list of str
            A list of filepaths, relative to static_path of all files
            (including those found in subdirectories)found. For example, if we
            are walking the css folder organized as follows:

                css/
                    common.css
                    other.css
                    subdir/
                        a.css
                        b.css
                    subdir2/
                        c.css

            The returned list would be:

                ['common.css', 'other.css', 'subdir/a.css', 'subdir/b.css',
                 'subdir2/c.css']
        """
        cwd = os.getcwd()
        files = [path.rpartition('/')[2] for path in
                 glob.glob(fmt % (cwd, static_path))
                 if os.path.isfile(path)]
        subdirs = [path.rpartition('/')[2] for path in
                   glob.glob(fmt % (cwd, static_path))
                   if os.path.isdir(path)]
        for subdir in subdirs:
            subfmt = fmt[:-1] + subdir + '/*'
            morepaths = BaseView.walk_paths(static_path, subfmt)
            files += ['%s/%s' % (subdir, path) for path in morepaths]
        return files
