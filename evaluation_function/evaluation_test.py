import unittest

try:
    from .evaluation import evaluation_function
except ImportError:
    from evaluation import evaluation_function

try:
    from .nlp_evaluation_tests import TestEvaluationFunction as NLPTestEvaluationFunction
except ImportError:
    from nlp_evaluation_tests import TestEvaluationFunction as NLPTestEvaluationFunction

try:
    from .slm_evaluation_tests import TestEvaluationFunction as SLMTestEvaluationFunction
except ImportError:
    from slm_evaluation_tests import TestEvaluationFunction as SLMTestEvaluationFunction

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
    """

    # NOTE: Parameter defining the metadata to be included in the response of the evaluation function
    include_test_data = True

    def test_returns_is_correct_true(self):
        response, answer, params = "A xor gate takes 2 inputs", "There are 2 inputs in a xor gate", dict(include_test_data=self.include_test_data)
        result = evaluation_function(response, answer, params)
        
        self.assertEqual(result.get("is_correct"), True)

    def test_reynolds_number_is_correct(self):
        answer, params = 'Density, Velocity, Viscosity, Length', dict(include_test_data=self.include_test_data)
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

            self.assertEqual(result.get("is_correct"), True, msg=f'{result}, Answer: {answer}, Response: {response}')

    def test_reynolds_number_is_incorrect(self):
        answer, params = 'Density, Velocity, Viscosity, Length', dict(include_test_data=self.include_test_data)
        incorrect_responses = [
            'density,,,',
            'rho,u,mu,L',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), False, msg=f'{result}, Answer: {answer}, Response: {response}')

    def test_reynolds_number_is_incorrect_with_keystring(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {'keystrings': [{'string': 'density'}, {'string': 'velocity'}, {'string': 'viscosity'}, {'string': 'length'}],
                                                                    'include_test_data': self.include_test_data}
        incorrect_responses = [
            'density,velocity,visc,',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), False, msg=f'{result}, Answer: {answer}')

    def test_reynolds_number_exact_match(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {
            'keystrings': [{'string': 'velocity', 'exact_match': True}],
            'include_test_data': self.include_test_data}
        incorrect_responses = [
            'density,speed,viscosity, length',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), False, msg=f'{result}, Answer: {answer}')

    def test_reynolds_number_should_not_contain(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {
            'keystrings': [{'string': 'direction', 'should_contain': False}],
            'include_test_data': self.include_test_data}
        incorrect_responses = [
            'density,speed,viscosity, length, direction',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), False, msg=f'{result}, Answer: {answer}')

    def test_reynolds_number_custom_feedback(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {
            'keystrings': [{'string': 'banana', 'custom_feedback': 'custom feedback with the word banana'}],
            'include_test_data': self.include_test_data}
        incorrect_responses = [
            'An incorrect response',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertIn('banana', result.get("feedback"), msg=f'{result}, Answer: {answer}')

    navier_stokes_answer = "The density of the film is uniform and constant, therefore the flow is incompressible. " \
                           "Since we have incompressible flow, uniform viscosity, Newtonian fluid, " \
                           "the most appropriate set of equations for the solution of the problem is the " \
                           "Navier-Stokes equations. The Navier-Stokes equations in Cartesian coordinates are used: " \
                           "mass conservation and components of the momentum balance"

    navier_stokes_params = {'keystrings': [{'string': 'Navier-Stokes equations'}, {'string': 'mass conservation'},
                                                                    {'string': 'momentum balance'}, {'string': 'incompressible flow'},
                                                                    {'string': 'uniform viscosity'}, {'string': 'Newtonian fluid'}],
                            'include_test_data': include_test_data }

    def test_navier_stokes_equation(self):
        answer, params = self.navier_stokes_answer, dict(include_test_data=self.include_test_data)
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
            self.assertEqual(result.get("is_correct"), True, msg=f'{result}, Answer: {answer}')

    def test_combined_evaluation_negation(self):
        answer, params = 'light blue', dict(include_test_data=self.include_test_data)
        correct_responses = [
            'not light blue', 
            'dark blue'       
        ]

        for response in correct_responses:
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get("is_correct"), False, msg=f'{result}, Answer: {answer}')

class TestEvaluationComputingFunction(unittest.TestCase):

    answer_networking_1 = "A networking algorithm is a set of rules or instructions designed to manage the operations of a computer network. These algorithms help in tasks like routing data between devices, managing traffic to avoid congestion, and ensuring data packets reach their destination efficiently and reliably."

    def test_networking_1_correct(self):
        answer = self.answer_networking_1
        responses = [
            "A networking algorithm is a method that helps in determining how data moves across a network, like deciding the best path for data packets to travel.",
            "Networking algorithms guide the way data is transferred through a network, making sure everything is sent smoothly and efficiently without congestion."
        ]
        params = {"include_test_data": True}

        for response in responses:
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get("is_correct"), True, msg=f'{result}, Answer: {answer}, Response: {response}')
    
    def test_networking_1_wrong(self):
        answer = self.answer_networking_1
        responses = [
            "A networking algorithm is the software used to connect computers to the internet, kind of like Wi-Fi or Bluetooth.",
            "A networking algorithm is a program that sends data from one computer to another.",
            "It’s a set of steps or instructions used in networks to control how information is sent and received between devices.", #similarity 0.69 < threshold , recommend to mention 'routing'
        ]
        params = {"include_test_data": True}

        for response in responses:
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get("is_correct"), False, msg=f'{result}, Answer: {answer}, Response: {response}')

    answer_ml_1 = "A Generative Adversarial Network (GAN) is a type of machine learning model composed of two neural networks: a generator and a discriminator. The generator creates fake data, while the discriminator tries to distinguish between real and fake data. Through this adversarial process, both networks improve over time, and the generator eventually becomes capable of producing data that closely resembles the real data."

    def test_ml_1_correct(self):
        answer = self.answer_ml_1
        responses = [
            "A GAN is a machine learning system with two networks: one generates fake data, and the other tries to spot the fake from the real, helping both improve.",
            "A GAN uses two neural networks that work against each other. The generator makes fake data, and the discriminator figures out if it’s real or fake."
        ]
        params = { 
            "keystrings": [{"string": "generator of fake data"}, {"string": "discriminates fake from real"}, {"string": "two neural networks"}],
            "include_test_data": True}

        for response in responses:
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get("is_correct"), True, msg=f'{result}, Answer: {answer}, Response: {response}')

    def test_ml_1_wrong(self):
        answer = self.answer_ml_1
        responses = [
            "A GAN is a type of algorithm used to detect fake data on the internet.",
            "A GAN is a network that generates data based on fake examples."
        ]
        params = {"include_test_data": True}

        for response in responses:
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get("is_correct"), False, msg=f'{result}, Answer: {answer}, Response: {response}')

    def test_ml_2_wrong(self):
        answer = self.answer_ml_1
        responses = [
            "It’s a model where two networks compete: one creates data, and the other tries to detect if it’s real or not. This makes the generator get better over time." # similarity of 0.71, not enough detail regarding 'generator of fake data'
        ]
        params = {
            "keystrings": [{"string": "generator of fake data"}, {"string": "discriminates fake from real"}, {"string": "two neural networks"}],
            "include_test_data": True}

        for response in responses:
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get("is_correct"), False, msg=f'{result}, Answer: {answer}, Response: {response}')

def load_tests(loader, tests, pattern):
    """
    Used to filter out which tests to run, if commented out then all unittests in the project will run.
    To run unittests:
        `python -m unittest app.evaluation_tests`
    """
    suite = unittest.TestSuite()
    
    # Add tests from submodules of unittest
    # suite.addTests(loader.loadTestsFromTestCase(NLPTestEvaluationFunction))     # test just NLP evaluation
    # suite.addTests(loader.loadTestsFromTestCase(SLMTestEvaluationFunction))     # test just SLM evaluation
    suite.addTests(loader.loadTestsFromTestCase(TestEvaluationFunction))        # test combined evaluation
    suite.addTests(loader.loadTestsFromTestCase(TestEvaluationComputingFunction)) # test combined evaluation

    return suite

if __name__ == '__main__':
    unittest.main()