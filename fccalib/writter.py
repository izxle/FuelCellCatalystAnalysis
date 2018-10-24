import pickle


def save_object(obj, filename):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
