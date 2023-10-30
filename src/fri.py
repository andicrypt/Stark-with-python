import math
from hashlib import blake2b

from finite_field import FieldElement
from merkle_tree import Merkle

class Fri:
    def __init__(self, offset, omega, initial_domain_length, expansion_factor, num_colinearity_tests):
        self.offset = offset
        self.omega = omega
        self.domain_length = initial_domain_length
        self.field = omega.field
        self.expansion_factor = expansion_factor
        self.num_colinearity_tests = num_colinearity_tests
        
    def num_rounds(self):
        codeword_length = self.domain_length
        num_rounds = 0
        while codeword_length > self.expansion_factor and 4 * self.num_colinearity_tests < codeword_length:
            codeword_length /= 2
            num_rounds += 1
        return num_rounds
    
    def eval_domain(self):
        return [self.offset * (self.omega^i) for i in range(self.domain_length)]

    def prove(self, codeword, proof_stream):
        assert(self.domain_length == len(codeword)), "initial codeword length does not match the length of initial codeword"

        # commit phase
        codewords = self.commit(codeword, proof_stream)
        
        # get indices
        top_level_indices = self.sample_indices(proof_stream.prover_fiat_shamir(), len(codewords[1]), len(codewords[-1]), self.num_colinearity_tests)
        indices = [index for index in top_level_indices]

        # query phase
        for i in range(len(codewords) - 1):
            indices = [index % (len(codewords[i]) // 2) for index in indices] # fold
            self.query(codewords[i], codewords[i+1], indices, proof_stream)

            return top_level_indices
        
    def commit(self, codeword, proof_stream, round_index=0):
        one = self.field.one()
        two = FieldElement(2, self.field)    
        omega = self.omega
        offset = self.offset
        codewords = []
        
        # for each round
        for r in range(self.num_rounds()):
            
            # compute and send Merkle root
            root = Merkle.commit(codeword)
            proof_stream.push(root)
            
            # prepare next round, if necessary
            if r == self.num_rounds() - 1:
                break
            
            # get challenge
            alpha = self.field.sample(proof_stream.prover_fiat_shamir())
            
            # collect codeword
            codewords += [codeword]

            # split and fold
            codeword = [two.inverse() * ( (one + alpha / (offset * (omega^i)) ) * codeword[i] + (one - alpha / (offset * (omega^i)) ) * codeword[len(codeword)//2 + i] ) for i in range(len(codeword)//2)]
            omega = omega^2
            offset = offset^2
            
        # send last codeword
        proof_stream.push(codeword)

        # collect last codeword too
        codewords = codewords + [codeword]
        
        return codewords
    
    def query(self, current_codeword, next_codeword, c_indices, proof_stream):
        # infer a and b indices
        a_indices = [index for index in c_indices]
        b_indices = [index + len(current_codeword)//2 for index in c_indices]

        # reveal leafs
        
    
        
        