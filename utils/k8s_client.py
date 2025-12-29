from kubernetes import client, config


def get_k8s_core_v1():
    """
    Load Kubernetes configuration automatically:
    - in-cluster OR
    - local kubeconfig
    """
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

    return client.CoreV1Api()
