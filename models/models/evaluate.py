from sklearn.metrics import (accuracy_score, roc_auc_score, confusion_matrix, 
                             precision_score, recall_score, brier_score_loss, log_loss)
import time
import json

def evaluate(model_name, map_name, pipeline, X_test, y_true, save_path = '../../outputs/evals'):
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    results = {
        'acc': accuracy_score(y_true, y_pred),
        'auc': roc_auc_score(y_true, y_prob),
        'confusion': confusion_matrix(y_true, y_pred),
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
        'brier': brier_score_loss(y_true, y_prob),
        'log': log_loss(y_true, y_prob)
    }

    print('')
    print(f'Computed Scores for {model_name} on {map_name}:')
    print('')
    print(f'{'Accuracy Score':<20} {results['acc']:>10.3f}')
    print(f'{'AUC Score:':<20} {results['auc']:>10.3f}')
    print(f'{'Precision Score':<20} {results['precicision']:>10.3f}')
    print(f'{'Recall Score':<20} {results['recall']:>10.3f}')
    print(f'{'Brier Score':<20} {results['brier']:>10.3f}')
    print(f'{'Log Score':<20} {results['log']:>10.3f}')
    print('')
    print(f'Confusion Matrix: \n', results['confusion'])

    timestamp = time.strftime("%H:%M:%S")
    save_str = f'/{model_name}_{map_name}_{timestamp}'
    save_dir = save_path+save_str
    json.dump(results, open(save_dir))
    print(f'Saved scores to {save_dir}!')

    return results