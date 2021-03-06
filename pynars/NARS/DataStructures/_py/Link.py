from enum import Enum
import enum
from pynars.Narsese import Item, Budget, Task, Term
from typing import List, Type, Union
from pynars.Narsese._py.Compound import Compound
from pynars.Narsese._py.Connector import Connector

from pynars.Narsese._py.Copula import Copula
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Truth import Truth
# from .Concept import *
from .Concept import *
# from . import Concept
from copy import copy, deepcopy
from pynars.NAL.Functions.ExtendedBooleanFunctions import *
from pynars.Config import Config

class LinkType(Enum):
    SELF = 0 # At C, point to C; TaskLink only 
    COMPONENT = 1 # At (&&, A, C), point to C
    COMPOUND = 2 # At C, point to (&&, A, C)
    COMPONENT_STATEMENT = 3 # At <C --> A>, point to C
    COMPOUND_STATEMENT = 4 # At C, point to <C --> A>
    COMPONENT_CONDITION = 5 # At <(&&, C, B) ==> A>, point to C
    COMPOUND_CONDITION = 6 # At C, point to <(&&, C, B) ==> A>
    TRANSFORM = 7 # At C, point to <(*, C, B) --> A>; TaskLink only
    TEMPORAL = 8 # At C, point to B, potentially without common subterm term

    def __int__(self):
        return self.value


class Link(Item):
    link_id = 0
    type: LinkType = None
    component_index: List[List[int]] # TODO: refer to OpenNARS 3.0.4, TermLink.java line 75 and TaskLink.java line 85. But why use it?
    def __init__(self, source: Type['Concept'], target: Task, budget: Budget, source_is_component: bool=None, copy_budget=True, index: list=None) -> None:
        self.link_id = Link.link_id
        self.component_index = tuple(index)

        hash_value = hash((source, target, self.component_index))
        super().__init__(hash_value, budget=budget,copy_budget=copy_budget)
        Link.link_id += 1
        
        self.source: Type['Concept'] = source
        self.target: Task = target

        
        self.source_is_component = source_is_component
        self.set_type(source_is_component)
    

    def set_type(self, source_is_component=None, type: LinkType=None, enable_transform=False):
        if type is not None:
            self.type = type
            return
        
        term_source: Term = self.source.term
        term_target: Term = self.target.term
        if source_is_component is None:
            source_is_component = term_source in term_target
            self.source_is_component = source_is_component
        
        # Identify the link-type according to the term-types of the source-term and the target-term.
        if source_is_component: 
            if term_target == term_source: self.type = LinkType.SELF
            elif term_target.is_statement:
                statement: Statement = term_target
                is_product_or_image = False
                if enable_transform: # only for tasklink
                    index = self.component_index
                    if len(index) >= 2:
                        statement_product: Statement = self.target.term[index[:-2]]
                        if statement_product.is_statement:
                            compound_product: Compound = statement_product[index[-2]]
                            if compound_product.is_compound:
                                if compound_product.connector in (Connector.Product, Connector.ExtensionalImage, Connector.IntensionalImage):
                                    is_product_or_image = True
                if is_product_or_image: self.type = LinkType.TRANSFORM
                else:
                    if term_target.is_statement and term_target.copula.is_higher_order:
                        #  in (Copula.Implication, Copula.Equivalence, Copula.PredictiveImplication, Copula.ConcurrentImplication, Copula.RetrospectiveImplication, Copula.PredictiveEquivalence, Copula.ConcurrentEquivalence):
                        if term_source == statement.subject or term_source == statement.predicate: self.type = LinkType.COMPOUND_CONDITION
                        else: self.type = LinkType.COMPOUND_STATEMENT
                    elif term_target.copula in (Copula.Inheritance, Copula.Similarity): self.type = LinkType.COMPOUND_STATEMENT
                    else: self.type = None
            elif term_target.is_compound: self.type = LinkType.COMPOUND
            else: self.type = None
            # self.component_index = Link.get_index(term_source, term_target)
        else:
            if term_source.is_statement:
                if term_source.copula in (Copula.Implication, Copula.Equivalence, Copula.PredictiveImplication, Copula.ConcurrentImplication, Copula.RetrospectiveImplication, Copula.PredictiveEquivalence, Copula.ConcurrentEquivalence):
                    statement: Statement = term_source
                    if term_target == statement.subject: self.type = LinkType.COMPONENT_STATEMENT
                    else: self.type = LinkType.COMPONENT_CONDITION
                elif term_source.copula in (Copula.Inheritance, Copula.Similarity): self.type = LinkType.COMPONENT_STATEMENT
                else: self.type = None
            elif term_source.is_compound: self.type = LinkType.COMPONENT
            else: self.type = None
            # self.component_index = Link.get_index(term_target, term_source)


    # @classmethod
    # def get_index(cls, term_component: Term, term_compound: Term):
    #     '''
    #     Get the index of term_component in term_compound,
    #     e.g. if term_component = A, term_compound = <(&,B,A)-->C>, then the index = [[0,1]]; if term_component = A, term_compound = <B==>A>, then the index = [[1]]; if term_component = A, term_compound = <(&,B,A)-->(&,A,C)>, then the index = [[0,1], [1,0]].
    #     '''
    #     def _get_index(term_component: Term, term_compound: Term, index: List[int]):
    #         index_new = []
    #         if term_compound.is_atom or term_component == term_compound:
    #             index_new.append([])
    #         elif term_compound.is_statement:
    #             statement: Statement = term_compound
    #             is_in_subject = False
    #             is_in_predicate = False
    #             if term_component in statement.subject:
    #                 is_in_subject = True
    #                 index_new.extend(
    #                     _get_index(term_component, statement.subject, [0])
    #                 )

    #             if term_component in statement.predicate:
    #                 is_in_predicate = True
    #                 index_new.extend(
    #                     _get_index(term_component, statement.predicate, [1])
    #                 )
                
    #             if not (is_in_subject or is_in_predicate): 
    #                 raise "Invalid case."

    #         elif term_compound.is_compound:
    #             compound: Compound = term_compound
    #             valid = False
    #             for i, component in enumerate(compound):
    #                 if term_component in component:
    #                     valid = True
    #                     index_new.extend(
    #                         _get_index(term_component, component, [i])
    #                     )
                        
    #             if not valid:
    #                 raise "Invalid case."
    #         else:
    #             raise "Invalid case."
    #         indexes = []
    #         for idx in index_new:
    #             indexes.append(index+idx)
    #         return indexes
    #     return _get_index(term_component, term_compound, [])


    # This is another implementation of `get_index` (,it may be a better one).
    @classmethod
    def get_index(cls, main_term: Union[Term, Statement, Compound], sub_term: Union[Term, Statement, Compound], index=None, indices=None):
        '''This function is temporary. The index of a term within another term should be obtained when constructing the latter one.'''

        if sub_term not in main_term: return None

        indices = [] if indices is None else indices
        index = [] if index is None else index

        if main_term == sub_term: 
            return indices.append(index)
        
        
        # if main_term.is_statement:
        #     if sub_term in main_term[0]: idx = 0
        #     elif sub_term in main_term[1]: idx = 1
        #     else: raise "Invalid case."
        #     index.append(idx)
        #     cls.get_index(main_term.terms[idx], sub_term, index, indices)
        if main_term.is_compound or main_term.is_statement:
            if sub_term in main_term:
                for idx, term in enumerate(main_term.terms):
                    # idx = main_term.terms.index(sub_term)
                    if sub_term in term:
                        index_copy = copy(index)
                        index_copy.append(idx)
                        cls.get_index(term, sub_term, index_copy, indices)
        # elif main_term.is_atom:
        #     pass
        else: raise "Invalid case."

        return indices

    @classmethod
    def update_budget(cls, budget: Budget, q: float, p_belief: float):
        budget.priority = min(1.0, Or(budget.priority, Or(q, p_belief)))
        budget.durability = min(1.0-Config.budget_epsilon, Or(budget.durability, q))



    @property
    def is_valid(self):
        return self.type is not None


    def __str__(self) -> str:
        return f'{self.budget} {(self.source)} --- {self.target}, {"+" if self.source_is_component else "-"}{self.component_index}'


class TermLink(Link):
    def __init__(self, source: Type['Concept'], target: Task, budget: Budget, source_is_component: bool=None, copy_budget=True, index: list=None) -> None:
        super().__init__(source, target, budget, source_is_component, copy_budget=copy_budget, index=index)

    def set_type(self, source_is_component=True, type: LinkType=None):
        Link.set_type(self, source_is_component, type)
        if not self.is_valid: self.type = None

    @property
    def is_valid(self):
        return self.type in (
            LinkType.COMPONENT, 
            LinkType.COMPOUND, 
            LinkType.COMPONENT_STATEMENT, 
            LinkType.COMPOUND_STATEMENT, 
            LinkType.COMPONENT_CONDITION, 
            LinkType.COMPOUND_CONDITION, 
            LinkType.TEMPORAL
        )

    def __str__(self) -> str:
        return f'{self.budget} {self.source.term} --- {self.target.term}, {"+" if self.source_is_component else "-"}{self.component_index}'

class TaskLink(Link):
    def __init__(self, source: Type['Concept'], target: Type['Concept'], budget: Budget, copy_budget=True, index: list=None) -> None:
        super().__init__(source, target, budget, True, copy_budget=copy_budget, index=index)

    def set_type(self, source_is_component=True, type: LinkType=None):
        Link.set_type(self, source_is_component, type, enable_transform=True)
        if not self.is_valid: self.type = None
    
    @property
    def is_valid(self) -> bool:
        return self.type in (
            LinkType.SELF, 
            LinkType.COMPOUND, 
            LinkType.COMPOUND_STATEMENT, 
            LinkType.COMPOUND_CONDITION, 
            LinkType.TRANSFORM, 
            LinkType.TEMPORAL
        )

    def __str__(self) -> str:
        return f'{self.budget} {self.source.term} --- {self.target.term}{self.target.sentence.punct.value}, {"+" if self.source_is_component else "-"}{self.component_index}'
    
        