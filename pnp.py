import pandas as pd
import tqdm


class Model:

    def __init__(self):
        self.population = self.set_population()
        self.constants = self.set_constants()
        self.functions = self.set_functions()

    def set_population(self):
        return {
        }

    def set_constants(self):
        return {
        }

    def set_functions(self):
        return {
        }

    def next_step(self, population, constants, functions, t):
        new_population = population.copy()

        for animal, number in population.items():
            new_population[animal] = functions[animal](population, constants)

        delta_population = {}

        for animal, number in population.items():
            delta_population[animal] = new_population[animal] * t
            population[animal] += delta_population[animal]
            population[animal] = population[animal]

        return population

    def run_simulation(self, steps, step_size):

        population = self.population.copy()
        constants = self.constants.copy()
        functions = self.functions.copy()
        
        population_development = [
            {
                'time': 0,
                'population': population.copy()
            }
        ]

        for step in tqdm.tqdm(range(1, steps+1)):
            population = self.next_step(population, constants, functions, step_size)
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

class LimitedFood(Model):
    
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

models = [SimpleModel, LimitedGrowth, LimitedFood]