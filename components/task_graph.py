import streamlit as st
import graphviz

def display_task_graph(tasks):
    """
    Display tasks and subtasks in a graph form using Graphviz.
    """
    graph = graphviz.Digraph(format="svg")
    graph.attr(rankdir="LR")  # Arrange the graph from left to right

    for task in tasks:
        # Add nodes for tasks
        graph.node(str(task["id"]), f'{task["name"]}\n({task["deadline"]})')

        # Add edges for subtasks
        if task["parent_task"]:
            graph.edge(str(task["parent_task"]), str(task["id"]))

    # Display the graph
    st.graphviz_chart(graph)
