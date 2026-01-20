import joblib
from sklearn.model_selection import train_test_split

from models.models.evaluate import evaluate
from models.models.pipeline import build_pipeline
from models.load.load_data import data_loader
from src.sql.create import create_connection

def train_map(model_name, map_name, X_train, y_train, output_path='../../outputs/models'):
    pipeline = build_pipeline(model_name)
    pipeline.fit(X_train, y_train)

    output_str = f'/{model_name}_{map_name}.joblib'
    output_dir = output_path + output_str
    joblib.dump(pipeline, output_dir)

    print(f'Saved trained pipeline to {output_path + output_str}')

    return pipeline

def train(model_name, data = None, output_path='../../outputs/models'):
    if not data:
        conn = create_connection
        df = data_loader(conn)
        X_train, y_train, X_test, y_test = train_test_split(df, test_size=.2, stratify=df['map_name'], random_state=42)

    map_names = data['map_name'].unique()

    print(f'Training {len(map_names)} unique maps')
    for map_name in map_names:
        train_mask = X_train['map_name'] = map_name
        test_mask = X_test['map_name'] = map_name

        X_train_map = X_train[train_mask]
        y_train_map = y_train[train_mask]
        X_test_map = X_test[test_mask]
        y_test_map = y_test[test_mask]

        pipeline = train_map(model_name, map_name, X_train_map, y_train_map, output_path)
        results = evaluate(model_name, map_name, pipeline, X_test_map, y_test_map)

    print(f'Training on {len(map_names)} unique maps completed!')