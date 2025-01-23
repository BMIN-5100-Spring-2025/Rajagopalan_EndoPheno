from clips import Symbol

def pull_facts(env):
    fact_message = ""
    cnt = 0
    for fact in env.facts():
        cnt += 1
        fact_message += str(fact)
        # fact_message.append("\n")
        # print(fact)
    fact_message += "Total facts: {}".format(cnt)
    return fact_message

def print_rules(env):
    cnt = 0
    for rule in env.rules():
        cnt += 1
        print(rule)
    print("Total rules: {}".format(cnt))

def print_templates(env):
    cnt = 0
    for template in env.templates():
        cnt += 1
        print(template)
    print("Total templates: {}".format(cnt))

# IPython notebook redirects stdin which prevents using clips "read" function to get user input
# this function builds a read_assert function for the input clips environment.
# The build function, read_assert, uses the Python "input" function to read user input and converts string input
# to appropriate type. 
# The prompt_map is a dictionary where keys are of the form template_name:slot_name and values
# are the prompts to display to the user when requesting input
# Exceptions are handled in try / except block to address input type and allowed value errors

def build_read_assert(env, prompt_map):

    def read_assert(template):
        try:
            temp = env.find_template(template)
            kwargs = {}
            for t in temp.slots:
                key = t.name
                prompt = prompt_map.get(f"{template}:{key}", f"Enter {template} {key}: ")
                val = input(prompt)
                if t.types[0] == "INTEGER":
                    val = int(val)
                elif t.types[0] == "FLOAT":
                    val = float(val)
                elif t.types[0] == "SYMBOL":
                    val = Symbol(val)
                kwargs[key] = val
    
            temp.assert_fact(**kwargs)
        except Exception as e:
            print(f"Invalid inputs provided for {template}:\n{e}")
    
    env.define_function(read_assert)
    
# this is needed for colab environment which doesn't work with native clips println function
# clips defrules in colab should use print_out in place of println
def build_print_out(env):

    def print_out(*args):
        line = ''
        for a in args:
            line = f'{line} {a}'
        print(line)
    
    env.define_function(print_out)
