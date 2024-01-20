#!/usr/bin/env python3
import re
import os
import read_conf
import sys

graph = str()


def read_and_filter_lines(file_path):
    decorators = dict()
    nodes = list()

    with open(file_path, 'r') as file:
        prev = ""
        for line in file:
            # Use the regex [^\t][^:]* to match lines that don't start with a tab and have any content after that
            if re.match(r'[^\t#].*:', line):
                label = line.strip()[:-1]
                decorators[label] = prev
            elif re.match(r'[^\t#][^:]*$', line):
                stripped_line = line.strip()
                if stripped_line!="":
                    if stripped_line.find("import") != 0:
                        nodes.append(stripped_line)
            prev = line

    return nodes,decorators

def gprint(content:str):
    global graph
    graph += content

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc == 1:
        print("Provide file name")
        exit()
    elif argc > 2:
        print("Too many arguments")
        exit()
    icons_images = read_conf.read_tags_and_images("./data.conf")

    file_path = sys.argv[1]  # Replace with your file path
    nodes,decorators = read_and_filter_lines(file_path)

    gv_nodes = []
    non_sequential_relations = str()

    #decorators=>  label : decorator
    #nodes =>  label +(args) (optional)

    gprint(r'''digraph G { 
        rankdir="LR";
        node [shape=box, style="rounded,filled,setlinewidth(0)",fontsize="10", fontcolor="gray24", fillcolor="gray88"];''')
    for node_cmd in nodes:
        node_name = read_conf.new_node_name()
        plain_cmd_flag = False
        for label, decorator in decorators.items(): #in function declarations
            if node_cmd.find(label) == 0:           #if identifier is the name of the function called
                gv_nodes.append(node_name)
                image_set_flag = False
                for tag, img in icons_images.items():  #in list of images and tags
                    if decorator.find(tag) != -1:      #if found a tag name matching decorator 
                        gprint(f"\t{node_name} [label=\"\",xlabel=\"{node_cmd}\",image=\"{img}\"];")
                        image_set_flag = plain_cmd_flag = True
                        break
                    elif node_cmd.find(tag) != -1:      #if found a tag name matching command 
                        gprint(f"\t{node_name} [label=\"\",xlabel=\"{node_cmd}\",image=\"{img}\"];")
                        image_set_flag = plain_cmd_flag = True
                        break
                if image_set_flag == False:
                        gprint(f"\t{node_name} [label=\"\",xlabel=\"{node_cmd}\",image=\"{icons_images['default']}\"];")
                        plain_cmd_flag = True
        if plain_cmd_flag == False:
            gv_nodes.append(node_name)
            for tag, img in icons_images.items():  #in list of images and tags
                if node_cmd.find(tag) != -1:      #if found a tag name matching command 
                    gprint(f"\t{node_name} [label=\"\",xlabel=\"{node_cmd}\",image=\"{img}\"];")
                    break
                else:
                    gprint(f"\t{node_name} [label=\"\",xlabel=\"{node_cmd}\",image=\"{icons_images['default']}\"];")
            
        
    gprint('\t' + '->'.join(gv_nodes) + ';')
    gprint("}")

    with open('.graph.gv', 'w') as file:
        file.write(graph)

    os.system("dot -Txlib .graph.gv")

