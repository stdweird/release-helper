"""
Label configuration
"""

import logging

def configure_labels(repo, labels):
    """
    Configure the labels of repository

    Labels is a mapping label name / color
    """

    existing_labels = dict([(l.name, l) for l in repo.get_labels()])

    logging.debug("Label configure for repo %s", repo.name)

    for label, color in labels.iteritems():
        if label in existing_labels:
            if existing_labels[label].color != color:
                existing_labels[label].edit(label, color)
                logging.debug("  Updated %s : %s", label, color)
        else:
            repo.create_label(label, color)
            logging.debug("  Added %s : %s", label, color)
