import xbmc
import xbmcgui
import xbmcplugin
import sys
import imp
import os

from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from metahandler import metahandlers
from metahandler import metacontainers
try:    import cPickle as pickle
except: import pickle

from utils import *

addon = Addon('plugin.video.waldo', sys.argv)
INDEXES_PATH   = os.path.join(addon.get_path(),'indexes')
PROVIDERS_PATH = os.path.join(addon.get_path(),'providers')

def listIndexes():
    import indexes
    for index in indexes.index_list:
        title = index.display_name
        args = {'mode':'ListIndexBrowsingOptions'}
        args['index'] = get_index_name(index)
        args['ind_path'] = os.path.dirname(index.__file__)
        print 'ind_path is %s' %args['ind_path']
        addon.add_directory(args,   {'title':  title})
    addon.end_of_directory()

def ListIndexBrowsingOptions(index, ind_path):
    print 'ind_path is %s' %ind_path
    index = import_module(index, fromlist=[INDEXES_PATH, ind_path])
    options = index.get_browsing_options()
    for option in options:
        callback = pickle.dumps(option['function'])
        args = pickle.dumps(option['kwargs'])
        addon.add_directory({'mode':'ActivateCallback', 'function':callback, 'kwargs':args, 'index':get_index_name(index), 'ind_path':ind_path},   {'title':option['name']})
    addon.end_of_directory()

def GetAllResults(type,title,year,imdb,tvdb,season,episode):
    import providers
    all_results = []
    for provider in providers.provider_list:
        results = provider.get_results(type,title,year,imdb,tvdb,season,episode)
        all_results.extend(results)
    for result in all_results:
        callback = pickle.dumps(result['function'])
        args = pickle.dumps(result['kwargs'])
        label = '[%s] %s' %(result['tag'],result['title'])
        addon.add_directory({'mode':'ActivateCallback', 'function':callback, 'kwargs':args},   {'title':label})
    addon.end_of_directory()

def ActivateCallback(function, kwargs, index, ind_path):
    if index:
        index = import_module(index, fromlist=[INDEXES_PATH, ind_path])
    callback = pickle.loads(function)
    kwargs = pickle.loads(kwargs)
    callback(**kwargs)

mode     = addon.queries.get('mode',    '')
index    = addon.queries.get('index',   '')
ind_path    = addon.queries.get('ind_path',   '')
name     = addon.queries.get('name',    '')
type     = addon.queries.get('type',    '')
title    = addon.queries.get('title',   '')
year     = addon.queries.get('year',    '')
imdb     = addon.queries.get('imdb',    '')
tvdb     = addon.queries.get('tvdb',    '')
season   = addon.queries.get('season',  '')
episode  = addon.queries.get('episode', '')
function = addon.queries.get('function','')
kwargs   = addon.queries.get('kwargs',  '')
receiver = addon.queries.get('receiver','')

addon.log(addon.queries)
if mode=='main':
    listIndexes()
elif mode=='ListIndexBrowsingOptions':
    ListIndexBrowsingOptions(index, ind_path)
elif mode=='GetAllResults':
    GetAllResults(type,title,year,imdb,tvdb,season,episode)
elif mode=='ActivateCallback':
    ActivateCallback(function,kwargs, index, ind_path)
elif mode=='CallModule':
    receiver = import_module(receiver, fromlist=[INDEXES_PATH,PROVIDERS_PATH, ind_path])
    receiver.callback(addon.queries)