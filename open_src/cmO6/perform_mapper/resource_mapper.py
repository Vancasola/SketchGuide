import os
from p4src import stub as st
import time
from perform_mapper import resource_extract as re
dir = "YOUR_DIR/open_src/cmO6/"
template_file = dir+"p4src/template.p4"
output_p4_file = dir+"p4src/p416_countmin_O6.p4"
resource_log_file = "SDE_DIR/build/p4-build/p416_countmin_O6/tofino/p416_countmin_O6/pipe/logs/mau.resources.log"
compile_sh = "YOUR_DIR/open_src/cmO6/p4src/compile_cm_O6.sh"
last_modify_time = 0
# generate the P4 program by replacing the stubs in the template file
def generate_p4(params):
    while(not os.path.exists(template_file)):
        time.sleep(1)
    p4_stub = st.stub()
    text = p4_stub.replace_stub(params)
    f_out = open(output_p4_file,"w")
    f_out.write(text)
    f_out.close()

# compile the reconfigured P4 program
def compile_p4(last_compile_time):
    # ensure the reconfigured P4 program is generated
    while(not os.path.exists(output_p4_file)):
        time.sleep(1)
    while(True):
        modify_time = os.path.getmtime(output_p4_file)
        if(modify_time <= last_compile_time):
            time.sleep(1)
        else:
            os.system(". " + compile_sh)
            time.sleep(3)
            while(not os.path.exists(resource_log_file)):
                time.sleep(1)
            return  os.path.getmtime(output_p4_file)

# extract the resource usage from the log file
def resource_extract(last_extract_time):
    while(not os.path.exists(resource_log_file)):
        time.sleep(1)
    while(True):
        modify_time = os.path.getmtime(resource_log_file)
        if(modify_time <= last_extract_time):
            time.sleep(1)
        else:
            res = re.get_resource_usage(resource_log_file)
            last_extract_time = modify_time
            return last_extract_time, res
