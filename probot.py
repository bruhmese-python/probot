#!/usr/bin/env python3
import re
import os
import read_conf
import sys
import tempfile

TITLE = 0
MAX_STR_LEN = 20

graph = str()
gv_nodes = []
secondary_relations = str()
secondary_attr = '[label=\"{}\",color=\"gray50\",fontname=\"Courier New\",fontsize=\"10\", fontcolor=\"gray24\"];'

sec_node_map = dict()


def read_and_filter_lines(file_path):
    def register_block():
        if 0!=len(block_stmts):
            blocks.append(block_stmts)
    decorators = dict()
    nodes = list()

    blocks = []
    with open(file_path, 'r') as file:
        prev = ""
        block_stmts = []
        for line in file:
            # Use the regex [^\t][^:]* to match lines that don't start with a tab and have any content after that
            if re.match(r'[^\t#].*:', line):        #label
                label = line.strip()[:-1]
                register_block()
                block_stmts = []
                block_stmts.append(label)
                decorators[label] = prev
            elif re.match(r'[^\t@#][^:]*$', line):  #main stmts
                stripped_line = line.strip()
                if stripped_line!="":
                    if stripped_line.find("import") != 0:
                        nodes.append(stripped_line)
            elif re.match(r'\t.*', line):           #block body
                stripped_line = line.strip()
                if stripped_line!="":
                    block_stmts.append(stripped_line)
            prev = line
    register_block()
    #[print(x) for x in blocks] 
    #print(decorators)

    return nodes,decorators,blocks

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

    real_file_path = ".smsh.tmp"
    os.system("/usr/local/bin/.smsh/macro_preprocessor.py "+file_path+" "+real_file_path)

    nodes,decorators,blocks = read_and_filter_lines(real_file_path)

    #decorators=>  label : decorator
    #nodes =>  label +(args) (optional)

    gprint(r'''digraph G { 
        graph [nodesep="1", ranksep="2",rankdir="LR", pack=false];
        node [shape=box, style="rounded,filled,setlinewidth(0)",forcelabels=true,fontname="Courier New",fontsize="10", fontcolor="gray24", fillcolor="gray88"];''')
    for block in blocks:
        side_nodes = []
        registered_head = False
        for node_cmd in block[1:]:
            node_name = read_conf.new_node_name()

            if not registered_head:
                sec_node_map[block[0]] = node_name
                registered_head = True

            side_nodes.append(node_name)
            t_len = len(node_cmd) 
            node_cmd = node_cmd[:min(MAX_STR_LEN,node_cmd.__len__())] 
            if t_len > MAX_STR_LEN:
                node_cmd = node_cmd + '...' 
            image_set_flag = False
            for tag, img in icons_images.items():  #in list of images and tags
                if node_cmd.find(tag) != -1:      #if found a tag name matching command 
                    gprint(f"\t{node_name} [label=\"\",xlabel=\"{node_cmd}\",image=\"{img}\"];")
                    image_set_flag = True
                    break
            if image_set_flag == False:
                gprint(f"\t{node_name} [label=\"\",xlabel=\"{node_cmd}\",image=\"{icons_images['default']}\"];")
        secondary_relations += '->'.join(side_nodes) + secondary_attr.format(" ")

    gprint(r'''node [shape=box, style="rounded,filled,setlinewidth(0)",forcelabels=true,fontname="Courier New",fontsize="10", fontcolor="gray24", fillcolor="gray88"];''')

    #main function
    for node_cmd in nodes:
        node_name = read_conf.new_node_name()
        plain_cmd_flag = False
        t_len = len(node_cmd) 
        og_node_cmd = node_cmd
        node_cmd = node_cmd[:min(MAX_STR_LEN,node_cmd.__len__())] 
        if t_len > MAX_STR_LEN:
            node_cmd = node_cmd + '...' 
        for label, decorator in decorators.items(): #in function declarations
            if node_cmd.find(label) == 0:           #if identifier is the name of the function called
                gv_nodes.append(node_name)
                args = og_node_cmd[len(label):]
                #print("\"" + args + "\"")
                secondary_relations +=  node_name + "->" +sec_node_map[label] + secondary_attr.format(args)      #join function name  and function call
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
            
        
    gprint('\t' + '->'.join(gv_nodes) + '[color="deepskyblue2"];')
    gprint('\n' + secondary_relations )
    gprint("}")

    with open('.graph.gv', 'w') as file:
        file.write(graph)

    os.system("dot -Txlib .graph.gv")

