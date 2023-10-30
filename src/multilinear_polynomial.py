from polynomial import Polynomial


class MultilinearPolynomial: 
    def __init__(self, dictionary):
        self.dictionary = dictionary
        
    def zero():
        return MultilinearPolynomial(dict())
    
    def __add__(self, other):
        dictionary = dict()
        num_variables = max([len(k) for k in self.dictionary.keys()] + [len(k) for k in other.dictionary.keys()])
        
        for k, v in self.dictionary.items():
            pad = list(k) + [0] * (num_variables - len(k))
            pad = tuple(pad)
            dictionary[pad] = v
        for k, v in other.dictionary.items():
            pad = list(k) + [0] * (num_variables - len(k))
            pad = tuple(pad)
            if pad in dictionary.keys():
                dictionary[pad] = dictionary[pad] + v
            else:
                dictionary[pad] = v
        return MultilinearPolynomial(dictionary)
    
    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        dictionary = dict()
        num_variables = max([len(k) for k in self.dictionary.keys()] + [len(k) for k in other.dictionary.keys()])
        
        for k0,v0 in self.dictionary.items():
            for k1,v1 in other.dictionary.items():
                exponent = [0] * num_variables
                for k in range(len(k0)):
                    exponent[k] += k0[k]
                for k in range(len(k1)):
                    exponent[k] += k1[k]
                exponent = tuple(exponent)
                if exponent in dictionary.keys():
                    dictionary[exponent] = dictionary[exponent] + v0 * v1
                else:
                    dictionary[exponent] = v0 * v1
        
        return MultilinearPolynomial(dictionary)
    
    def __neg__(self):
        dictionary = dict()
        for k, v in self.dictionary.items():
            dictionary[k] = -v
        return MultilinearPolynomial(dictionary)
    
    def __xor__(self, exponent):
        if self.is_zero():
            return MultilinearPolynomial(dict())
        field = list(self.dictionary.values())[0].field
        num_variables = len(list(self.dictionary.keys())[0])
        exp = [0] * num_variables
        acc = MultilinearPolynomial({tuple(exp): field.one()})
        for b in bin(exponent)[2:]:
            acc = acc * acc
            if b == '1':
                acc = acc * self
        return acc
        
    
    def constant(element):
        return MultilinearPolynomial({tuple([0]): element})
    
    def is_zero(self):
        if not self.dictionary:
            return True
        else:
            for v in self.dictionary.values():
                if v.is_zero() == False:
                    return False
            return True    

    def variables(num_variables, field):
        variables = []
        for i in range(num_variables):
            exponent = [0] * i + [1] + [0] * (num_variables - i - 1)
            variables = variables + [MultilinearPolynomial({tuple(exponent): field.one()})]
        return variables
    
    def lift(polynomial, variable_index):
        if polynomial.is_zero():
            return MultilinearPolynomial(dict())
        field = polynomial.coefficients[0].field
        variables = MultilinearPolynomial.variables(variable_index + 1, field)
    
        x = variables[-1]
        acc = MultilinearPolynomial(dict())
        for i in range(len(polynomial.coefficients)):
            acc = acc + MultilinearPolynomial.constant(polynomial.coefficients[i]) * (x^i)
        return acc 
    
    def evaluate(self, point):
        acc = point[0].field.zero()
        for k, v in self.dictionary.items():
            prod = v
            for i in range(len(k)):
                prod = prod * (point[i] ^ k[i])
            acc = acc + prod
        return acc
    
    def evaluate_symbolic(self, point):
        acc = Polynomial([])
        for k,v in self.dictionary.items():
            prod = Polynomial([v])
            for i in range(len(k)):
                prod = prod * (point[i] ^ k[i])
            acc = acc + prod
        return acc
    
    