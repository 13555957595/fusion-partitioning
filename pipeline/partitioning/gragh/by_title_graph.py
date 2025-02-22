from neo4j import GraphDatabase
import json

# Neo4j 连接信息
URI = "bolt://localhost:7687"  # Neo4j 服务器的 URI
USER = "neo4j"  # 用户名
PASSWORD = "Dlut0411"  # 密码

def create_element_relationship(tx, data):
    count = 0
    for item in data:
        tx.run(
            """
            MERGE (n:Text {element_id: $element_id})
            SET n.element_body = $element_body
            """,
            element_id=item["element_id"],
            element_body=json.dumps(item, ensure_ascii=False)
        )
        # 如果存在父节点，则创建关系
        if item["metadata"]["parent_id"]:
            tx.run(
                """
                MATCH (parent:Text {element_id: $parent_id})
                MATCH (child:Text {element_id: $element_id})
                MERGE (parent)-[:HAS_CHILD]->(child)
                """,
                parent_id=item["metadata"]["parent_id"],
                element_id=item["element_id"]
            )
        count = count + 1
    print(count)
def do(output_partition_jsonfile: str, driver):
    with open(output_partition_jsonfile, 'r', encoding='utf-8') as file:
        data = json.load(file)

    with driver.session() as session:
        session.execute_write(create_element_relationship, data)

# 主程序
if __name__ == "__main__":
    # 创建驱动连接
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        # 调用 do 函数
        do("../../.cache/456.pdf/_partition.json", driver)
    finally:
        # 关闭连接
        driver.close()