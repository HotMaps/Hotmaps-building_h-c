# -*- coding: utf-8 -*-

from flask import Flask
import sys
import pip


application = Flask(__name__)

@application.route('/', methods=['GET'])
def index():
    modules = 'List of installed modules:\n'
    for i in pip.utils.get_installed_distributions(local_only=True):
        modules = modules + '\n' + i.project_name + ' ' + i.version
    return 'HotMaps-building_h-c' + ' running Python ' + sys.version + ', using virutalenv: ' + str(hasattr(sys, 'real_prefix')) + '\n<pre>' + modules + '</pre>'

def test():
    application.run(debug=True)

if __name__ == '__main__':
    test()
