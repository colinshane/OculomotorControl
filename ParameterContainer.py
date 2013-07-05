import os
import json

class ParameterContainer(object):
    """
    This class contains the simulation parameters in a dictionary called params.
    """

    def __init__(self, params_fn=None):
        if params_fn == None:
            self.params = {}
            self.set_filenames()
        else:
            self.load_params_from_file(params_fn)


    def set_param_dict(self, name, params):
        """A sub-dictionary params is set to the given name
        Keyword arguments:
        name -- (str) name of the sub-dictionary
        params -- (dict) the parameter dictionary
        """
        self.params[name] = params


    def set_folder_name(self, folder_name=None):
        """
        Set the root folder name where results will be stored.

        Keyword arguments:
        folder_name -- string
        """

        if folder_name == None:
            folder_name = 'DefaultFolder/'
            self.params['folder_name'] = folder_name
        else:
            self.params['folder_name'] = folder_name
        print 'Folder name:', self.params['folder_name']


    def set_filenames(self, folder_name=None):
        """
        Set all filenames and subfolders.

        Keyword arguments
        folder_name -- string
        """

        self.set_folder_name(folder_name)

        self.params['parameters_folder'] = "%sParameters/" % self.params['folder_name']
        self.params['figures_folder'] = "%sFigures/" % self.params['folder_name']
        self.params['tmp_folder'] = "%stmp/" % self.params['folder_name']
        self.params['data_folder'] = '%sData/' % (self.params['folder_name']) # for storage of analysis results etc
        self.params['folder_names'] = [self.params['folder_name'], \
                            self.params['parameters_folder'], \
                            self.params['figures_folder'], \
                            self.params['tmp_folder'], \
                            self.params['data_folder']]

        self.params['params_fn_json'] = '%ssimulation_parameters.json' % (self.params['parameters_folder'])


    def create_folders(self):
        """
        Must be called from 'outside' this class before the simulation
        """

        for f in self.params['folder_names']:
            if not os.path.exists(f):
                print 'Creating folder:\t%s' % f
                os.system("mkdir %s" % (f))


    def load_params_from_file(self, fn):
        """
        Loads the file via json from a filename
        Returns the simulation parameters stored in a file 
        Keyword arguments:
        fn -- file name
        """
        f = file(fn, 'r')
        print 'Loading parameters from', fn
        self.params = json.load(f)
        return self.params



    def update_values(self, to_update):
        """
        Updates the parameters given in to_update and sets the filenames
        Keyword arguments:
        to_update -- dictionary storing the parameters to be updated
        """
        for key, value in kwargs.iteritems():
            self.params[key] = value
        # update the possibly dependent parameters
        self.set_filenames()



    def write_parameters_to_file(self, fn=None, params=None):
        """
        Keyword arguments:
        fn -- (optional) target output filename for json dictionary
        params -- (optional) the modified parameter dictionary that is to write
        """

        if fn == None:
            fn = self.params['params_fn_json']
        if params == None:
            params_to_write = self.params
        if not (os.path.isdir(params_to_write['folder_name'])):
            print 'Creating folder:\n\t%s' % params_to_write['folder_name']
            self.create_folders(params_to_write)
        print 'Writing parameters to: %s' % (fn)
        output_file = file(fn, 'w')
        d = json.dump(params_to_write, output_file)



