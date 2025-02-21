import json

from neo4j import GraphDatabase

from pipeline.partitioning.element import Element

# Neo4j连接配置
uri = "bolt://localhost:7687"  # Neo4j服务器地址
username = "neo4j"             # 用户名
password = "Dlut0411"     # 密码

# 连接到Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))

with open('../output/partition_output.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    print(data);



def create_text_relationship(tx, element:Element):
    # 创建或更新当前节点
    tx.run(
        """
        MERGE (n:Text {element_id: $element_id})
        SET n.text = $text,
            n.last_modified = $last_modified,
            n.page_number = $page_number,
            n.languages = $languages,
            n.file_directory = $file_directory,
            n.filename = $filename,
            n.filetype = $filetype
        """,
        element_id=element.element_id,
        text=element.text,
        last_modified=element.metadata.last_modified,
        page_number=element.metadata.page_number,
        languages=element.metadata.languages,
        file_directory=element.metadata.file_directory,
        filename=element.metadata.filename,
        filetype=element.metadata.filetype
    )

    # 如果存在父节点，则创建关系
    if element.metadata.parent_id:
        tx.run(
            """
            MATCH (parent:Text {element_id: $parent_id})
            MATCH (child:Text {element_id: $element_id})
            MERGE (parent)-[:HAS_CHILD]->(child)
            """,
            parent_id=element.metadata.parent_id,
            element_id=element.element_id
        )

# def create_image_relationship(tx, element:Element):
#     # 创建或更新当前节点
#     tx.run(
#         """
#         MERGE (n:Text {element_id: $element_id})
#         SET n.text = $text,
#             n.last_modified = $last_modified,
#             n.page_number = $page_number,
#             n.languages = $languages,
#             n.file_directory = $file_directory,
#             n.filename = $filename,
#             n.filetype = $filetype
#         """,
#         element_id=element.element_id,
#         text=element.text,
#         last_modified=element.metadata.last_modified,
#         page_number=element.metadata.page_number,
#         languages=element.metadata.languages,
#         file_directory=element.metadata.file_directory,
#         filename=element.metadata.filename,
#         filetype=element.metadata.filetype,
#         image_path=element.metadata
#     )
#
#     # 如果存在父节点，则创建关系
#     if element.metadata.parent_id:
#         tx.run(
#             """
#             MATCH (parent:Text {element_id: $parent_id})
#             MATCH (child:Text {element_id: $element_id})
#             MERGE (parent)-[:HAS_CHILD]->(child)
#             """,
#             parent_id=element.metadata.parent_id,
#             element_id=element.element_id
#         )

# 执行操作
with driver.session() as session:
    session.execute_write(create_text_relationship, data)

# 关闭连接
driver.close()