def pad_labels(labels, min_label_size, align='center'):
    """Pad labels to the same size

    Parameters
    ----------
    labels: list
        list of labels
    min_label_size: int
        minimum size of the labels
    align: str
        alignment of the labels

    Returns
    -------
    new_labels: list
        list of padded labels

    """
    new_labels = []
    for label in labels:
        num = len(label)
        if num < min_label_size:
            if align == 'center':
                label = label.center(min_label_size)
            elif align == 'left':
                label = label.ljust(min_label_size)
            elif align == 'right':
                label = label.rjust(min_label_size)
        elif num > min_label_size:
            label = label[:min_label_size]

        new_labels.append(label)
    return new_labels
