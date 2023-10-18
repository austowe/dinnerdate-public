from collections import Counter

def dict_to_tuple(d):
    return tuple(sorted(d.items()))

def find_common_elements(list_of_lists):
    if not list_of_lists:
        return []

    # Convert the first embedded list into a set of tuples
    shared_items = {tuple(item.items()) for item in list_of_lists[0]}

    # Find the intersection with each subsequent list
    for sublist in list_of_lists[1:]:
        shared_items.intersection_update({tuple(item.items()) for item in sublist})

    # Convert back to dictionaries before returning the result
    return [dict(item) for item in shared_items]

def find_top_elements(lists, n):
    # Flatten the list of lists and count occurrences of elements
    flattened = [dict_to_tuple(item) for sublist in lists for item in sublist]
    element_counts = Counter(flattened)
    
    # Get the n most common elements
    most_common = element_counts.most_common(n)
    
    # Calculate the percentage of lists each element appears in
    total_lists = len(lists)
    common_with_percentage = [(dict(element), count/total_lists * 100) for element, count in most_common]
    
    return common_with_percentage