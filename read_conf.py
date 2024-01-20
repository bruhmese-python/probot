c_name = 'A'
n_name = 0

def new_node_name():
    global c_name,n_name
    if c_name == 'Z':
        c_name = 'A'
        n_name += 1
    t_c_name = c_name
    c_name = chr(ord(c_name)+1) 
    return str(t_c_name + str(n_name))

def read_tags_and_images(file_path):
    tag_image_dict = {}

    with open(file_path, 'r') as file:
        for line in file:
            # Split each line into tag and image name
            tag, image_name = map(str.strip, line.split(':'))

            # Store in the dictionary
            tag_image_dict[tag] = image_name

    return tag_image_dict
