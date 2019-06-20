import os_utils as os_utils
from obspy.core import UTCDateTime
import xarray as xr
import json

def write(xarray, path, extension):
    array_path      = '{}{}{}{}'.format(path,os_utils.sep,extension,'.nc')
    attributes_path = '{}{}{}{}'.format(path,os_utils.sep,extension,'.metadata.json')
    data = xarray.copy()
    data.attrs = {}
    data.to_netcdf(array_path)
    with open(attributes_path, 'w') as p_file:
        json.dump(xarray.attrs, p_file)


def read(path, extension):
    xarray_path     ='{}{}{}{}'.format(path,os_utils.sep,extension,'.nc')
    attributes_path ='{}{}{}{}'.format(path,os_utils.sep,extension,'.metadata.json')
    xarray = xr.open_dataset(xarray_path)
    with open(attributes_path, 'r') as p_file:
        attrs = json.load(p_file)
    xarray.attrs = attrs
    return xarray


class _IO:

    def __init__(self, dir):
        self._file      = dir
        self._isenabled = False

    def enable(self):
        self._isenabled=True

    def is_enabled(self):
        return self._isenabled

    def get_folder_extension(self, xarray):
        if 'stacks' in xarray.attrs.keys():
            # then xarray represents stack data
            pair = list(xarray.coords['pair'].values)[0]
            stack_num = str(xarray.attrs['stacks'])
            return self._file + os_utils.sep + pair + os_utils.sep + stack_num
        elif 'operations' in xarray.attrs.keys():
            # then xarray represents single station data
            operation = xarray.attrs['operations'].split('\n')[-1]
            starttime = UTCDateTime(xarray.attrs['starttime']).isoformat()
            return self._file + os_utils.sep + operation + os_utils.sep + starttime
        else:
            # then xarray is a dataset
            pair_list = list(xarray.coords['pair'].values)
            strsum = pair_list[0] + '|' + str(len(pair_list))
            return self._file + os_utils.sep + strsum

    def get_filename(self, xarray):
        if 'stacks' in xarray.attrs.keys():
            # then xarray represents stack data
            starttime = UTCDateTime(xarray.attrs['starttime']).isoformat()
            return starttime
        elif 'operations' in xarray.attrs.keys():
            # then xarray represents single station data
            station = list(xarray.coords['station_id'].values)[0]
            return station
        else:
            return 'combined_data'


class _XArrayWrite(_IO):

    def __init__(self, directory=None):
        super().__init__(dir)

    def set_folder(self, file):
        self.enable()
        if not os_utils.folder_exists(file):
            os_utils.make_dir(file)
        self._file = file

    def _chkmkdir(self,dir):
        if not os_utils.folder_exists(dir):
            os_utils.make_dir(dir)

    def __call__(self, xarray,one,two,three, dask_client=None, **kwargs):
        if self._file is not None:
            folder    = '{}{}{}{}{}'.format(self._file,os_utils.sep,one,os_utils.sep,two)
            self._chkmkdir(folder)
            write(xarray, folder, three)


class _XArrayRead(_IO):

    def __init__(self, directory=None):
        super().__init__(directory)
        self._file = directory

    def set_folder(self, directory):
        self.enable()
        if not os_utils.folder_exists(directory):
            os_utils.make_dir(directory)
        self._file = directory

    def __call__(self,xarray, extension1, extension2, file, dask_client=None, **kwargs):
        result = None
        if self._file is not None:
            folder = self._file + os_utils.sep + extension1 + os_utils.sep + extension2
            result = read(folder, file)

        if result is not None:
            return result
        else:
            return xarray

class _XDaskTask:

    def __init__(self,verbosity=0,dummy_task=False,**kwargs):
        self._kwargs = kwargs
        self._kwargs['verbosity']=verbosity
        self._kwargs['dummy_task']=dummy_task
        self.read  = _XArrayRead(None)
        self.write = _XArrayWrite(None)
        self._enabled = True

    def disable(self):
        self._enabled=False

    def set_folder(self, folder, action,**kwargs):
        if action=='write':
            self.write.set_folder(folder)
        else:
            self.read.set_folder(folder)


    def set_param(self,kwarg):
        for key, value in kwarg.items():
            if key in self._kwargs.keys():
                self._kwargs[key]=value
            else:
                print('given key is not a selectable parameter')

    def __call__(self, *args, starttime=0, station=0, dask_client=None, **kwargs):
        result = None
        if self._enabled:
            if dask_client is None:
                if not self.read.is_enabled():
                    persist_name       = self._get_name(*args)
                    persisted_metadata = self._metadata_to_persist(*args,**kwargs)
                    result             = self._single_thread_execute(*args,**kwargs)
                    self._assign_metadata(persist_name, persisted_metadata, result)
            else:
                result = self._dask_task_execute(*args, dask_client=dask_client,**kwargs)

        result = self._io_operations(args, dask_client, result, starttime, station)
        return result

    def _assign_metadata(self, persist_name, persisted_metadata, result):
        if persisted_metadata is not None:
            result.attrs = persisted_metadata
        if persist_name is not None:
            result.name = persist_name

    def _io_operations(self, args, dask_client, result, starttime, station):
        if self.read.is_enabled():
            result = self.read(args[0], self._get_process(), self._time_signature(starttime), station,
                               dask_client=dask_client)
            result = self._addition_read_processing(result)
        elif self.write.is_enabled():
            self.write(result, self._get_process(), self._time_signature(starttime), station, dask_client=dask_client)
        return result

    def _time_signature(self,time):
        return UTCDateTime(int(time*100)/100.0).isoformat()

    def _single_thread_execute(self,*args,**kwargs):
        pass

    def _dask_task_execute(self,*args,**kwargs):
        pass


    def _metadata_to_persist(self, *param, **kwargs):
        if len(param)==1:
            attrs = param[0].attrs.copy()
        else:
            attrs = {**param[0].attrs.copy(), **param[1].attrs.copy()}
        added_kv_metadata = self._add_metadata_key()
        add_operation     = self._add_operation_string()
        if added_kv_metadata is not None:
            if isinstance(added_kv_metadata[0],tuple) or isinstance(added_kv_metadata[0],list):
                for key, value in added_kv_metadata:
                    attrs[added_kv_metadata[0]] = added_kv_metadata[1]
            else:
                attrs[added_kv_metadata[0]] = added_kv_metadata[1]
        if add_operation is not None:
            attrs['operations']=attrs['operations'] + '\n' + add_operation
        return attrs

    def _add_operation_string(self):
        return None
            
    def _add_metadata_key(self):
        return None

    def _get_name(self,*args):
        if len(args) == 1:
            name = args[0].name
        else:
            name = args[0].name + ':' + args[1].name
        return name

    def _get_process(self):
        return 'process'

    def _addition_read_processing(self, result):
        return result


class XArrayProcessor(_XDaskTask):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def _addition_read_processing(self, result):
        name   = list(result.data_vars)[0]
        xarray       = result[name].copy()
        xarray.attrs = result.attrs.copy()
        del result
        return xarray


class XDatasetProcessor(_XDaskTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _addition_read_processing(self, result):
        return result