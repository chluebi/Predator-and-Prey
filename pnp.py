import pandas as pd
import tqdm
import math
import copy

def prune(df, factor):
    df = df.copy()

    first = df.copy()[df['time'] == 0].iloc[0, 0]
    second = df.copy()[df['time'] > 0].iloc[0, 0]
    distance = first - second

    df = df[(df['time']/distance) % factor == 0]
    return df


class ModelSeries:

    def __init__(self, model, r):
        self.model = copy.deepcopy(model)
        self.iter = iter(r)

    def change_property(self):
        next(self.iter)

    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            self.change_property(self)
            seperate_df, combined_df = self.model.run_simulation()
            return seperate_df, combined_df
        except StopIteration:
            raise StopIteration
            
     
class Model:

    methods = [
        'Euler',
        'Ralston'
    ]

    def __init__(self):
        self.simulation_parameters = self.set_simulation_parameters()
        self.population = self.set_population()
        self.constants = self.set_constants()
        self.functions = self.set_functions()
        self.discrete = self.set_discrete()
        self.method = self.set_method()

    def set_simulation_parameters(self):
        return {
            'steps': 1000,
            'step_size': 10**-2,
            'compression': 1,
            'verbose': True
        }

    def set_population(self):
        return {
        }

    def set_constants(self):
        return {
        }

    def set_functions(self):
        return {
        }

    def set_discrete(self):
        return False

    def set_method(self):
        return Model.methods[0]


    def next_step(self, population, constants, functions, t):
        d_population = {}
        new_population = {}

        if self.discrete:
            for animal, number in population.items():
                d_population[animal] = functions[animal](population, constants)
                new_population[animal] = d_population[animal]
        elif self.method == 'Euler':
            for animal, number in population.items():
                d_population[animal] = functions[animal](population, constants)
                population[animal] += d_population[animal] * t
        elif self.method == 'Ralston':
            d_population1 = {}
            for animal, number in population.items():
                d_population1[animal] = functions[animal](population, constants)

            population2 = {}
            population2 = {key: value + 2/3 * t * d_population1[key] for key, value in population.items()}

            d_population2 = {}
            for animal, number in population.items():
                d_population2[animal] = functions[animal](population2, constants)

            for animal, number in population.items():
                population[animal] += t * (1/4 * d_population1[animal] + 3/4 * d_population2[animal])
        else:
            raise Exception(f'Not a valid method provided (method "{method}" is not defined)')
                        
        return population

    def run_simulation(self):

        population = self.population.copy()
        constants = self.constants.copy()
        functions = self.functions.copy()

        steps = self.simulation_parameters['steps']
        step_size = self.simulation_parameters['step_size']
        compression = self.simulation_parameters['compression']
        verbose = self.simulation_parameters['verbose']
        
        population_development = [
            {
                'time': 0,
                'population': population.copy()
            }
        ]

        if verbose:
            it = tqdm.tqdm(range(1, steps+1))
        else:
            it = range(1, steps+1)
            
        for step in it:
            population = self.next_step(population, constants, functions, step_size)
            if step % compression == 0:
                population_development.append({
                    'time': step*step_size,
                    'population': population.copy()
                })


        single_population_development = {
            'time': []
            }

        for animal, amount in population.items():
            single_population_development[animal] = []

        for time_step in population_development:
            single_population_development['time'].append(time_step['time'])
            for animal, amount in time_step['population'].items():
                single_population_development[animal].append(amount)
        

        combined_population_development = {
            'time': [],
            'animal_type': [],
            'animal_number': []
            }

        for time_step in population_development:
            for animal, amount in time_step['population'].items():
                combined_population_development['time'].append(time_step['time'])
                combined_population_development['animal_type'].append(animal)
                combined_population_development['animal_number'].append(amount)

        #print(single_population_development)
        #print(combined_population_development)
        return pd.DataFrame(single_population_development), pd.DataFrame(combined_population_development)

    def print_parameters(self):
        
        steps = self.simulation_parameters['steps']
        step_size = self.simulation_parameters['step_size']
        compression = self.simulation_parameters['compression']

        rows = ['\\begin{table}[]', '\\begin{tabular}{llllllll|}', '\\hline']
        rows.append('\\multicolumn{2}{{|l|}}{Simulation} & \\multicolumn{2}{l|}{Population} & \\multicolumn{2}{l|}{Functions} & \\multicolumn{2}{l|}{Constants} \\\\ \\hline')

        row_amount = max(len(self.population.items()), len(self.constants.items()), len(self.functions.items()))

        for i in range(row_amount):
            if i == 0:
                row = '\\multicolumn{{1}}{{|l|}}{{Steps}} & \\multicolumn{{1}}{{|l|}}{{{0}}}'.format(steps)
            elif i == 1:
                row = '\\multicolumn{{1}}{{|l|}}{{Step Size}} & \\multicolumn{{1}}{{|l|}}{{{0}}}'.format(step_size)
            elif i == 2:
                row = '\\multicolumn{{1}}{{|l|}}{{Compression}} & \\multicolumn{{1}}{{|l|}}{{{0}}}'.format(compression)
            else:
                row = '&'

            row += ' & '

            if i < len(self.population.items()):
                animal, number = list(self.population.items())[i]
                row += '\\multicolumn{{1}}{{|l|}}{{{0}}} & \\multicolumn{{1}}{{|l|}}{{{1}}}'.format(animal, number)
            else:
                row += '&'

            row += ' & '

            if i < len(self.functions.items()):
                animal, function = list(self.functions.items())[i]
                row += '\\multicolumn{{1}}{{|l|}}{{{0}}} & \\multicolumn{{1}}{{|l|}}{{$x$}}'.format(animal)
            else:
                row += '&'

            row += ' & '

            if i < len(self.constants.items()):
                constant, value = list(self.constants.items())[i]
                row += '\\multicolumn{{1}}{{|l|}}{{{0}}} & \\multicolumn{{1}}{{|l|}}{{{1}}}'.format(constant, value)
            else:
                row += '&'

            row += ' \\\\ '

            

            if i+1 == 3:
                row += '\\cline{1-2}'
            if i+1 == len(self.population.items()):
                row += '\\cline{3-4}'
            if i+1 == len(self.functions.items()):
                row += '\\cline{5-6}'
            if i+1 == len(self.constants.items()):
                row += '\\cline{7-8}'

            rows.append(row)

        rows.append('\\end{tabular}')
        rows.append('\\end{table}')

        return '\n'.join(rows)
                
        t = '''\\begin{table}[]
\\begin{tabular}{ll|l|l|l|l|ll}
\\hline
\\multicolumn{2}{|l|}{Simulation} & \\multicolumn{2}{l|}{Population} & \\multicolumn{2}{l|}{Functions} & \\multicolumn{2}{l|}{Constants} \\\\ \\hline
\\multicolumn{1}{|l|}{Steps} & steps & Animal1 & animal & f1 & $x$ & \\multicolumn{1}{l|}{C1} & \\multicolumn{1}{l|}{c1} \\\\ \\hline
\\multicolumn{1}{|l|}{Step Size} & step\\_size & Animal2 & animal & f2 & $x$ & \\multicolumn{1}{l|}{C2} & \\multicolumn{1}{l|}{c2} \\\\ \\hline
\\multicolumn{1}{|l|}{Compression} & compression & Animal3 & animal & f3 & $x$ & \\multicolumn{1}{l|}{C3} & \\multicolumn{1}{l|}{c3} \\\\ \\hline
 &  & Animal4 & animal & f4 & $x$ &  &  \\\\ \\cline{3-6}
\\end{tabular}
\\end{table}'''

    def print_vertical_parameters(self):
        steps = self.simulation_parameters['steps']
        step_size = self.simulation_parameters['step_size']
        compression = self.simulation_parameters['compression']

        t = '''
\\begin{{table}}[]
\\begin{{tabular}}{{|l|l}}
\\cline{{1-1}}
Simulation &  \\\\ \\hline
steps & \\multicolumn{{1}}{{l|}}{{ {0} }} \\\\ \\hline
step Size & \\multicolumn{{1}}{{l|}}{{ {1} }} \\\\ \\hline
compression & \\multicolumn{{1}}{{l|}}{{ {2} }} \\\\ \\hline
Population &  \\\\ \\hline \n'''.format(steps, step_size, compression)

        for animal, number in self.population.items():
            t += '{0} & \\multicolumn{{1}}{{l|}}{{ {1} }} \\\\ \\hline \n'.format(animal, number)

        t += 'Constants &  \\\\ \\hline \n'

        for constant, value in self.constants.items():
            t += '{0} & \\multicolumn{{1}}{{l|}}{{ {1} }} \\\\ \\hline \n'.format(constant, value)

        t += 'Functions &  \\\\ \\hline \n'

        for animal, function in self.functions.items():
            t += '{0} & \\multicolumn{{1}}{{l|}}{{ $x + x^2$ }} \\\\ \\hline \n'.format(animal, function)

        t += '''\\end{{tabular}}
\\end{{table}}'''.format('tabular', 'table')

        return t




class SimpleModel(Model):

    def set_population(self):
        return {
        'rabbit': 1,
        'wolf': 1
        }

    def set_constants(self):
        return {
            'rabbit-r': 1, # 1
            'hunt': 1, #1
            'rabbit-value': 1, #1
            'wolf-hunger': 1 #1
        }

    def set_functions(self):
        return {
            'rabbit': lambda population, constants: population['rabbit'] * (constants['rabbit-r'] - constants['hunt'] * population['wolf']),
            'wolf': lambda population, constants: population['wolf'] * (constants['rabbit-value'] * population['rabbit'] - constants['wolf-hunger'])
        }


class LimitedGrowth(Model):
    def set_population(self):
        return {
        'rabbit':1,
        'wolf':1
        }

    def set_constants(self):
        return {
            'rabbit-r': 1,
            'max-rabbit-growth': 0.001,
            'wolf-hunt': 1,
            'max-wolf-growth': 0.001,
            'rabbit-value': 1, 
            'wolf-hunger': 1
        }

    def set_functions(self):
        return {
            'rabbit': lambda population, constants: population['rabbit'] * min(constants['max-rabbit-growth'], (constants['rabbit-r'] - constants['wolf-hunt'] * population['wolf'])),
            'wolf': lambda population, constants: population['wolf'] * min(constants['max-wolf-growth'], (constants['rabbit-value'] * population['rabbit'] - constants['wolf-hunger']))
        }

class Grass(Model):
    
    def set_population(self):
        return {
        'grass': 1,
        'rabbit': 1,
        'wolf': 1
        }

    def set_constants(self):
        return {
            'grass-r': 1,
            'rabbit-hunt': 1,
            'grass-value': 1,
            'rabbit-hunger': 0.5,
            'wolf-hunt': 0.5,
            'rabbit-value': 1,
            'wolf-hunger': 1
        }

    def set_functions(self):
        return {
            'grass': lambda population, constants: population['grass'] * (constants['grass-r'] - constants['rabbit-hunt'] * population['rabbit']),
            'rabbit': lambda population, constants: population['rabbit'] * (constants['grass-value'] * population['grass'] - constants['rabbit-hunger'] - constants['wolf-hunt'] * population['wolf']),
            'wolf': lambda population, constants: population['wolf'] * (constants['rabbit-value'] * population['rabbit'] - constants['wolf-hunger'])
        }


class NicholsonBailey(Model):

    def set_population(self):
        return {
        'rabbit': 1,
        'wolf': 1
        }

    def set_constants(self):
        return {
            'rabbit-r': 1, # 1
            'hunt': 1, #1
            'rabbit-value': 1, #1
            'wolf-hunger': 1 #1
        }

    def set_functions(self):
        return {
            'rabbit': lambda population, constants: constants['rabbit-r'] * population['rabbit'] * math.exp(- constants['hunt'] * population['wolf']),
            'wolf': lambda population, constants: constants['rabbit-value'] * population['rabbit'] * (1 - math.exp(- constants['hunt'] * population['wolf']))
        }

    def set_discrete(self):
        return True


models = [SimpleModel, LimitedGrowth, Grass, NicholsonBailey]