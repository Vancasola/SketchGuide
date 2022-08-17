This is github repository for SketchGuide.

# Quick Start
You can first modify the path and reconfigure a CM-sketch optimized by [SketchLib](https://github.com/SketchLib/P4_SketchLib) O6 using SketchGuide.
## Step 1
Install [bayesian-optimization](https://github.com/fmfn/BayesianOptimization)

    $ pip install bayesian-optimization


## Step 2
You should modify these paths in the following files in your environment.
- ./cmO6/p4src/compile_cm_O6.sh
  - dir = YOUR_DIR/open_src/
  - script_home = SDE_DIR
- ./cmO6/perform_mapper/resource_mapper.py 
  - dir = "YOUR_DIR/open_src/cmO6"
  - resource_log_file = "/SDE_DIR/build/p4-build/p416_countmin_O6/tofino/p416_countmin_O6/pipe/logs/mau.resources.log"
  - compile_sh = "YOUR_DIR/open_src/cmO6/P4src/compile_cm_O6.sh"

## Step 3
Then, you can run the supervisor file to automatically generate sketch skyline candidates

    $ python3 supervisor.py

## Step 4
Last, you can solve the final sketch skyline results

    $ python3 skylines.py

You can see file "skyline_results.log" is generated.

# Tutorial
- You can leverage SketchGuide to reconfigure your sketches.
## Step 1
- Write a P4 program that can be successfully compiled. e.g., ./p4src/p416_countmin_O6.p4.
- Write a sketch program that can output the accuracy results, e.g., ./perform_mapper/accuracy_mapper.py.
## Step 2
- Identify the resource parameters (referring to the primitives in our paper).
- Replace the parameters that you want to configure as a stub, and generate a P4 template file, e.g., ./p4src/template.p4
- Modify the ./p4src/stub.py, which can identify the stubs and replace the stubs as new parameters so that a completed P4 program can be generated.
## Step 3
- Set the parameter range of sketches in the ./config/config.json, the parameter range can be relatively large because the Bayesian Optimizer will solve and narrow down the range later.
- Set the weight of each metric that your want to optimize. The Bayesian Optimizer will combine these metrics as a linear combination and maximize this combination.
- Set the bound of results. You can budget the resources and filter the unsatisfactory results here.
## Step 4
- Modify the input parameter of black_box_function in ./supervisor.py, e.g., def black_box_function(reg_size, hash_cnt, hash_tbl_size, exact_tbl_size)
- Modify the accuracy mapper for your parameters, e.g., recall, precision = am.accuracy_mapper(params['reg_size'], params['hash_cnt'], params['hash_tbl_size'], params['exact_tbl_size'])
- Keep the same parameter order as the one in ./config/config.json
- Adjust the maximal metric value in fuction get_max_metric_val (supervisor.py) to normalized the objective function.
- Choose the rounds of bayesian optimization in function optimized_params = solve_candidate(init_points = 10, n_iter = 40), 10 randomly search.
## Step 5
- Run supervisor.py to generate SS candidates.
- Run skylines.py to solve the final SS results.