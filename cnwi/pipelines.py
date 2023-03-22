from . import imgs
from . import sfilters
from . import td
from . import derivatives as driv

from .eelib import eefuncs


def pipeline(training_data, s2 = None, s1 = None dem = None):
    """Runs a standard Random Forest Classification

    Args:
        training_data (_type_): _description_
        optical (_type_, optional): _description_. Defaults to None.
        sar (_type_, optional): _description_. Defaults to Nonedem=None.
    """
    
    """
    Pipeline will follow this pattern
    take s1, s2, dem inputs do some pre-processing
    
    create stack to sample from
    
    generate samples to train model
    
    create the rf model
    
    train tf model
    
    classify the stack
    
    create an output class, training_samples (with geometry maintained), classified image 
    """
    # prep the inputs
    s1s = [imgs.Sentinel1(_) for _ in s1]
    # sar inputs
    boxcar = sfilters.boxcar(1)
    sar_pp1 = eefuncs.batch_despeckle(s1s, boxcar)
    
    # sar derivatives
    ratios = driv.batch_create_ratio(
        images=sar_pp1,
        numerator='VV',
        denominator='VH'
    )
    
   
    

    