import unittest
from pathlib import Path

from mgate_keeper import MGateKeeper


class _FakeCompletions:
    def __init__(self):
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return {"ok": True}


class _FakeChat:
    def __init__(self):
        self.completions = _FakeCompletions()


class _FakeClient:
    def __init__(self):
        self.chat = _FakeChat()


class MGateKeeperTests(unittest.TestCase):
    def test_project_resources_resolve_relative_to_project_file(self):
        client = _FakeClient()
        project = Path("mgate_keeper/projects/photosynthesis.mg8")
        keeper = MGateKeeper(project_file=str(project), client=client)

        self.assertEqual(len(keeper.gates), 2)
        self.assertIsNotNone(keeper.context)
        self.assertEqual(keeper.context.context_id, "CTX_PHOTOSYNTHESIS")

    def test_query_injects_gates_and_gst_context(self):
        client = _FakeClient()
        keeper = MGateKeeper(
            project_file="mgate_keeper/projects/photosynthesis.mg8",
            client=client,
        )

        keeper.query("What is photosynthesis?")
        kwargs = client.chat.completions.last_kwargs

        self.assertIsNotNone(kwargs)
        self.assertEqual(kwargs["temperature"], 0)
        self.assertEqual(kwargs["seed"], 42)
        self.assertEqual(kwargs["messages"][1]["content"], "What is photosynthesis?")

        control = kwargs["messages"][0]["content"]
        self.assertIn("G_PHOTOSYNTHESIS", control)
        self.assertIn("CTX_PHOTOSYNTHESIS", control)
        self.assertIn("Be precise and accurate", control)
        self.assertIn("must explain the process in scientifically correct terms", control)


if __name__ == "__main__":
    unittest.main()
