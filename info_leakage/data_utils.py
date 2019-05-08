import csv
import os
import sys

import numpy as np
import logging as log
import pickle


def ready_logger():
    """
    Prepare python logging object.
    Modify this function to customize logging behavior
    """
    class LessThanFilter(log.Filter):
        def __init__(self, exclusive_maximum, name=""):
            super(LessThanFilter, self).__init__(name)
            self.max_level = exclusive_maximum

        def filter(self, record):
            # non-zero return means we log this message
            return 1 if record.levelno < self.max_level else 0

    # Get the root logger
    logger = log.getLogger()

    # Have to set the root logger level, it defaults to logging.WARNING
    logger.setLevel(log.NOTSET)

    logging_handler_out = log.StreamHandler(sys.stdout)
    logging_handler_out.setLevel(log.DEBUG)
    logging_handler_out.addFilter(LessThanFilter(log.WARNING))

    logging_handler_err = log.StreamHandler(sys.stderr)
    logging_handler_err.setLevel(log.WARNING)

    format = log.Formatter('[%(asctime)s][%(processName)-10s][%(levelname)s] %(message)s')
    logging_handler_err.setFormatter(format)
    logging_handler_out.setFormatter(format)

    # add handlers to logger
    logger.addHandler(logging_handler_err)
    logger.addHandler(logging_handler_out)

    # return the prepared logger
    return logger


# logging object to be used throughout the application
logger = ready_logger()


class WebsiteData(object):
    """
    Object-wrapper to conveniently manage dataset
    """
    def __init__(self, X, Y):
        self._X = X
        self._Y = Y
        self.features = range(X.shape[1])
        self.sites = range(len(np.unique(self._Y)))

    def __len__(self):
        return self._X.shape[0]

    def get_labels(self):
        """
        Return Y
        """
        return np.copy(self._Y)

    def get_site(self, label, feature=None):
        """
        Return X for given site. Optionally, also filter by feature.
        """
        f = [True if y == label else False for y in self._Y]
        if feature is not None:
            return np.copy(self._X[f, feature])
        return np.copy(self._X[f, :])

    def get_feature(self, feature):
        """
        Return all X for a specific feature
        """
        return np.copy(self._X[:, feature])


def load_data(directory, extension='.csv', delimiter=' '):
    """
    Load feature files from feature directory.
    :return X - numpy array of data instances w/ shape (n,f)
    :return Y - numpy array of data labels w/ shape (n,1)
    """
    # load pickle file if it exist
    feat_pkl = os.path.join(directory, "features.pkl")
    if os.path.exists(feat_pkl):
        with open(feat_pkl, "rb") as fi:
            X, Y = pickle.load(fi)
            return X, Y
    else:
        X = []  # feature instances
        Y = []  # site labels
        for root, dirs, files in os.walk(directory):

            # filter for feature files
            files = [fi for fi in files if fi.endswith(extension)]

            def isfloat(element):
                try:
                    float(element)
                    return True
                except ValueError:
                    return False

            # read each feature file as CSV
            for file in files:
                #cls, ins = file.split("-")
                cls, ls = file.split("_")
                with open(os.path.join(root, file), "r") as csvFile:
                    features = list(csv.reader(csvFile, delimiter=delimiter))
                    features = [[float(f) if isfloat(f) else 0 for f in instance if f] for instance in features]

                    if len(features) >= 500:
                        features = features[:500]

                        X.extend(features)
                        Y.extend([int(cls)-1 for _ in range(len(features))])

        labels = list(set(Y))
        labels.sort()
        d = dict()
        for i in range(len(labels)):
            d[labels[i]] = i
        Y = list(map(lambda x: d[x], Y))

        # save dataset to pickle file for quicker future loading
        X, Y = np.array(X), np.array(Y)
        with open(feat_pkl, "wb") as fi:
            pickle.dump((X, Y), fi)

    # return X and Y as numpy arrays
    return X,Y

