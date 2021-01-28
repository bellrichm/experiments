# v0.0.2
import os
import resource
import time

import Cheetah.Template

if __name__=="__main__":
    def genit(filename, genname):
        tmpname = genname + '.tmp'

        #print("  compiling")
        compiled_template = Cheetah.Template.Template(
            file=filename,
        )

        #print("  respond")
        unicode_string = compiled_template.respond()

    def touch_file(filename):
        os.system("touch %s" % filename)

    def get_data(page_size, calls):
        record = {}
        record['call'] = calls
        record['timeStamp'] = time.time()
        try:
            #---- from Tom ---
            pid = os.getpid()
            procfile = "/proc/%s/statm" % pid
            try:
                mem_tuple = open(procfile).read().split()
            except (IOError, ):
                return
                # Unpack the tuple:
            (size, resident, share, text, lib, data, dt) = mem_tuple
            mb = 1024 * 1024
            record['mem_size']  = float(size)     * page_size / mb
            record['mem_rss']   = float(resident) * page_size / mb
            record['mem_share'] = float(share)    * page_size / mb
       	    #---- from Tom ---
        except (ValueError, IOError, KeyError) as e:
            logerr('memory_info failed: %s' % e)

        return record

    page_size = resource.getpagesize()
    template = "index.html.tmpl"
    include = "large_file.inc"
    genname = "output.html"
    calls = 0
    max_calls = 100
    record = get_data(page_size, calls)
    print(record)
    while calls < max_calls:
        calls += 1
        # comment out the call to touch_file for a 'static' file test
        touch_file(include)
        genit(template,genname)
        record = get_data(page_size, calls)
        print(record)

