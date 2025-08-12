
from scipy.stats import kendalltau
from scipy import stats
import numpy as np

# Category F1s for two systems
original = np.array([0.9721, 0.9322, 0.9139])      # original_brat
consist = np.array([0.9753,0.9249,0.9182]) # consistent
markov = np.array([0.9721,0.9247,0.9274]) # markov
random = np.array([0.9748, 0.9343, 0.9261])    # syn.random
simple = np.array([0.9686,0.9259,0.936])    # simple
neg_control = np.array([0.8686,0.2259,0.736])    # negative control
pos_control = np.array([0.9721, 0.9321, 0.9142])      # positive control

# Ranked F1
ranked5_original = np.array([2,3,1]) 
ranked5_consist = np.array([4,2,2]) 
ranked5_markov = np.array([2,1,4]) 
ranked5_random = np.array([3,4,3]) 
ranked5_simple = np.array([1,3,5]) 

ranked4_original = np.array([1,3,1]) 
ranked4_consist = np.array([3,2,2]) 
ranked4_markov = np.array([1,1,4]) 
ranked4_random = np.array([2,4,3]) 

def print_kendall_tau(name,values,hips_only='False'):
   #print("\n"+str(values))
   if hips_only is True:
      tau, p_value = kendalltau(ranked5_original, values)
   else:
      tau, p_value = kendalltau(ranked5_original, values)
   print(f"{name} Kendall's Tau: {tau:.4f}")
   print(f"p-value: {p_value:.4f}")


print("All strategies")
print_kendall_tau('markov',ranked5_markov)
print_kendall_tau('random',ranked5_random)
print_kendall_tau('simple',ranked5_simple)
#print_kendall_tau('neg_control',neg_control)
#print_kendall_tau('pos_control',pos_control)
print("\n")
print("HIP strategies only")
print_kendall_tau('consistent',ranked4_consist,True)
print_kendall_tau('markov',ranked4_markov,True)
print_kendall_tau('random',ranked4_random,True)


print(stats.kruskal(original,consist,markov,random,simple))
