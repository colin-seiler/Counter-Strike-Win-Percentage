import yaml
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

PARAM_PATH = '../cfg/model_params.yaml'
PARAMS = yaml.safe_load(open(PARAM_PATH, 'r'))

MODEL_REGISTRY = {
    'rf': RandomForestClassifier,
    'xgb': XGBClassifier,
    'lgbm': LGBMClassifier,
}

MAP_COORDS = {
    'Ancient': {'x': 0, 'y': 0, 'z': 0},
    'Anubis': [],
    'Dust II': [],
}

def map_coordinate_fixer(df):
    df = df.copy()
    df = df[df['map_name'].isin(MAP_COORDS)]

    maps_in_df = df['map_name'].unique()

    coord_cols = {
        'x': [f'{team}{i}_x' for team in ['ct', 't'] for i in range(1, 6)],
        'y': [f'{team}{i}_y' for team in ['ct', 't'] for i in range(1, 6)],
        'z': [f'{team}{i}_z' for team in ['ct', 't'] for i in range(1, 6)]
    }
    
    for map_name in maps_in_df:
        mask = df['map_name'] == map_name
        offset = MAP_COORDS[map_name]

        df.loc[mask, coord_cols['x']] -= offset['x']
        df.loc[mask, coord_cols['y']] -= offset['y']
        df.loc[mask, coord_cols['z']] -= offset['z']
    
    return df

def build_pipeline(model_name):
    if model_name not in MODEL_REGISTRY:
        raise ValueError("Please provide model_name of xgb, rf, or lgbm")

    return Pipeline([
        ('fix_coords', FunctionTransformer(map_coordinate_fixer)),
        ('model', MODEL_REGISTRY[model_name](**PARAMS[model_name]))
    ])