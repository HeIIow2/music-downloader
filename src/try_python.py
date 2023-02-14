from typing import Optional


class TreeNode:
    """A class representing a binary tree node."""

    def __init__(self, val: int = 0, left: Optional['TreeNode'] = None, right: Optional['TreeNode'] = None):
        """
        Initializes a new instance of the TreeNode class.

        Args:
            val: The value of the node.
            left: The left child of the node.
            right: The right child of the node.
        """
        self.val = val
        self.left = left
        self.right = right


def invert_tree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    """
    Inverts a binary tree.

    Args:
        root: The root node of the binary tree.

    Returns:
        The root node of the inverted binary tree.
    """
    if root is None:
        return None

    # Swap left and right children of the root node
    root.left, root.right = root.right, root.left

    # Recursively invert the left and right subtrees
    invert_tree(root.left)
    invert_tree(root.right)

    return root
