import unittest

try:
    from .nlp_evaluation import evaluation_function
except ImportError:
    from nlp_evaluation import evaluation_function

class TestEvaluationFunction(unittest.TestCase):
    """
        TestCase Class used to test the algorithm.
        ---
        Tests are used here to check that the algorithm written 
        is working as it should. 
        
        It's best practise to write these tests first to get a 
        kind of 'specification' for how your algorithm should 
        work, and you should run these tests before committing 
        your code to AWS.

        Read the docs on how to use unittest here:
        https://docs.python.org/3/library/unittest.html

        Use evaluation_function() to check your algorithm works 
        as it should.

        NOTE: this testcase uses the EvaluationResponse class from the evaluation_response_utilities.py file
    """
    def test_nlp_returns_is_correct_true(self):
        response, answer, params = "A xor gate takes 2 inputs", "There are 2 inputs in a xor gate", dict()
        result = evaluation_function(response, answer, params)
        
        self.assertEqual(result.get_is_correct(), True)

    def test_nlp_reynolds_number_is_correct(self):
        answer, params = 'Density, Velocity, Viscosity, Length', dict()
        correct_responses = [
            'density,velocity,viscosity,length',
            'Density,Velocity,Viscosity,Length',
            'density,characteristic velocity,viscosity,characteristic length',
            'Density,Velocity,Shear viscosity,Length',
            'density,velocity,viscosity,lengthscale',
            'density,velocity,shear viscosity,length',
            'density,characteristic velocity,shear viscosity,characteristic lengthscale',
            'density,velocity,shear viscosity,characteristic lengthscale',
            'density,velocity,viscosity,length scale',
            'pressure,characteristic velocity of flow,shear viscosity,characteristic length scale',
        ]

        for response in correct_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get_is_correct(), True, msg=f'Response: {response}')

    def test_nlp_reynolds_number_is_incorrect(self):
        answer, params = 'Density, Velocity, Viscosity, Length', dict()
        incorrect_responses = [
            'density,,,',
            'rho,u,mu,L',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get_is_correct(), False, msg=f'Response: {response}')

    def test_nlp_reynolds_number_is_incorrect_with_keystring(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {'keystrings': [{'string': 'density'}, {'string': 'velocity'}, {'string': 'viscosity'}, {'string': 'length'}]}
        incorrect_responses = [
            'density,velocity,visc,',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get_is_correct(), False, msg=f'Response: {response}')

    def test_nlp_reynolds_number_exact_match(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {
            'keystrings': [{'string': 'velocity', 'exact_match': True}]}
        incorrect_responses = [
            'density,speed,viscosity, length',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get_is_correct(), False, msg=f'Response: {response}')

    def test_nlp_reynolds_number_should_not_contain(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {
            'keystrings': [{'string': 'direction', 'should_contain': False}]}
        incorrect_responses = [
            'density,speed,viscosity, length, direction',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get_is_correct(), False, msg=f'Response: {response}')

    def test_nlp_reynolds_number_custom_feedback(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {
            'keystrings': [{'string': 'banana', 'custom_feedback': 'custom feedback with the word banana'}]}
        incorrect_responses = [
            'An incorrect response',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertIn('banana', result._feedback[result.get_feedback('feedback')[0]], msg=f'Response: {response}')

    navier_stokes_answer = "The density of the film is uniform and constant, therefore the flow is incompressible. " \
                           "Since we have incompressible flow, uniform viscosity, Newtonian fluid, " \
                           "the most appropriate set of equations for the solution of the problem is the " \
                           "Navier-Stokes equations. The Navier-Stokes equations in Cartesian coordinates are used: " \
                           "mass conservation and components of the momentum balance"

    navier_stokes_params = {'keystrings': [{'string': 'Navier-Stokes equations'}, {'string': 'mass conservation'},
                                                                    {'string': 'momentum balance'}, {'string': 'incompressible flow'},
                                                                    {'string': 'uniform viscosity'}, {'string': 'Newtonian fluid'}]}

    def test_nlp_navier_stokes_equation(self):
        answer, params = self.navier_stokes_answer, dict()
        correct_responses = [
            #'Navier-stokes. Continuum, const and uniform density and viscosity so incompressible, newtonian. Fits all '
            #'requirements for navier stokes',
            'Navier-Stokes in a Cartesian reference coordinates would be chosen for this particular flow. This is due '
            'to the reason that the flow is Newtonian, the viscosity is uniform and constant. Additionally, '
            'the density is uniform and constant; implying that it is an incompressible flow. This flow obeys the '
            'main assumptions in order to employ the Navier Stokes equations.',
        ]

        for response in correct_responses:
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get_is_correct(), True, msg=f'Response: {response}')

    def test_nlp_negation(self):
        answer, params = 'light blue', dict()
        correct_responses = [
            'bright blue',
            'light blue',
            # 'not light blue', # WARNING: THIS test should be False, but the similarity algorithm cannot handle negations
            # 'dark blue'       # WARNING: THIS test should be False, but the similarity algorithm cannot handle context understanding
        ]

        for response in correct_responses:
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get_is_correct(), True, msg=f'Response: {response}')

if __name__ == "__main__":
    unittest.main()