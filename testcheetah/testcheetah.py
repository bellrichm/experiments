#!/usr/bin/env python3
'''
Learning Cheetah internals
'''

# v0.0.3

import gc
import os
import resource
import sys
import time

import Cheetah.Template

if __name__=="__main__":

    def genit(filename):
        ''' Process the template '''

        #print("  compiling")
        #template_instance = Cheetah.Template.Template(file=filename)
        compiler_settings = {'useNameMapper': False,
                             'useSearchList': False,
                             'useFilters': False,
                            }

        template_class = Cheetah.Template.Template.compile(file=filename,
                                                           #returnAClass=False,
                                                           cacheCompilationResults=False,
                                                           keepRefToGeneratedCode=False,
                                                           useCache=False,
                                                           compilerSettings=compiler_settings,
                                                          )

        template_instance = template_class()

        # print("  respond")
        unicode_string = template_instance.respond()
        template_instance.shutdown()
        #del template_instance
        gc.collect()
        print(sys.modules)
        #del template_instance
        #print(unicode_string)

        #print("   end")

    def touch_file(filename):
        ''' Update file modified date/time. '''
        os.system("touch %s" % filename)

    def get_data(page_size, calls):
        ''' Get memory data.'''
        record = {}
        record['call'] = calls
        record['timeStamp'] = time.time()
        try:
            pid = os.getpid()
            procfile = "/proc/%s/statm" % pid
            try:
                mem_tuple = open(procfile).read().split()
            except (IOError, ):
                return

            size, resident, share, *_ = mem_tuple
            mega = 1024 * 1024
            record['mem_size']  = float(size)     * page_size / mega
            record['mem_rss']   = float(resident) * page_size / mega
            record['mem_share'] = float(share)    * page_size / mega
        except (ValueError, IOError, KeyError) as exception:
            print('memory_info failed: %s' % exception)

        return record

    def main():
        ''' mainline '''
        page_size = resource.getpagesize()
        template = "index.html.tmpl"
        include = "large_file.inc"
        #include = "wrapper.inc"
        # template = include # do not bother with include - compile large file directly
        calls = 0
        max_calls = 100
        record = get_data(page_size, calls)
        print(record)
        while calls < max_calls:
            calls += 1
            # comment out the call to touch_file for a 'static' file test
            touch_file(include)
            genit(template)
            record = get_data(page_size, calls)
            print(record)

    main()
