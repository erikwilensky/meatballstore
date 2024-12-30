import graphviz
import streamlit as st


def display_task_graph(tasks):
    """Display tasks and subtasks in a graph form using Graphviz."""
    graph = graphviz.Digraph(format="svg")
    graph.attr(rankdir="LR")  # Arrange the graph from left to right

    for task in tasks:
        graph.node(str(task["id"]), f'{task["name"]}\n({task["deadline"]})')
        if task["parent_task"]:
            graph.edge(str(task["parent_task"]), str(task["id"]))

    st.graphviz_chart(graph)
