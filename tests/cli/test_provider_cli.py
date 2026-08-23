from yasinai.cli.provider import create_parser


def test_provider_cli_parser_supports_required_commands():
    parser = create_parser()
    assert parser.parse_args(["list"]).action == "list"
    assert parser.parse_args(["setup"]).action == "setup"
    assert parser.parse_args(["use", "gateway"]).name == "gateway"
    assert parser.parse_args(["test", "gateway"]).name == "gateway"
    assert parser.parse_args(["remove", "gateway"]).name == "gateway"
