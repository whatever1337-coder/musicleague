"use strict";

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var VoteControl = function (_React$Component) {
    _inherits(VoteControl, _React$Component);

    function VoteControl(props) {
        _classCallCheck(this, VoteControl);

        var _this = _possibleConstructorReturn(this, (VoteControl.__proto__ || Object.getPrototypeOf(VoteControl)).call(this, props));

        _this.state = {
            uri: props.uri,
            points: 0
        };
        return _this;
    }

    _createClass(VoteControl, [{
        key: "render",
        value: function render() {
            var stateClass = this.state.points < 0 ? "downVoted" : this.state.points > 0 ? "upVoted" : "";
            return React.createElement(
                "div",
                { className: "col-md-4 voteControl" + " " + stateClass },
                React.createElement(
                    "div",
                    { className: "voteControlInner" },
                    React.createElement("span", { className: "downButton", onClick: this.downVote.bind(this) }),
                    React.createElement(
                        "span",
                        { className: "pointCount" },
                        Math.abs(this.state.points)
                    ),
                    React.createElement("span", { className: "upButton", onClick: this.upVote.bind(this) }),
                    React.createElement(
                        "div",
                        { className: "statusIconWrapper" },
                        React.createElement("span", { className: "statusIcon" })
                    )
                )
            );
        }
    }, {
        key: "downVote",
        value: function downVote() {
            var newPointValue = this.state.points - 1;
            if (this.props.minPoints == null || newPointValue >= this.props.minPoints) {
                var downVoteAllowed = this.props.onDownVote(this.state.uri, newPointValue);
                if (downVoteAllowed) this.setState({ points: this.state.points - 1 });
            } else {
                console.log("Down vote count " + Math.abs(newPointValue) + " exceeds per-song allowance. Rejecting.");
            }
        }
    }, {
        key: "upVote",
        value: function upVote() {
            var newPointValue = this.state.points + 1;
            if (this.props.maxPoints == null || newPointValue <= this.props.maxPoints) {
                var upVoteAllowed = this.props.onUpVote(this.state.uri, newPointValue);
                if (upVoteAllowed) this.setState({ points: this.state.points + 1 });
            } else {
                console.log("Up vote count " + newPointValue + " exceeds per-song allowance. Rejecting.");
            }
        }
    }]);

    return VoteControl;
}(React.Component);

var SongInfo = function (_React$Component2) {
    _inherits(SongInfo, _React$Component2);

    function SongInfo(props) {
        _classCallCheck(this, SongInfo);

        var _this2 = _possibleConstructorReturn(this, (SongInfo.__proto__ || Object.getPrototypeOf(SongInfo)).call(this, props));

        _this2.state = {
            uri: props.uri,
            track: { name: '',
                artists: [{ name: '' }],
                album: { images: [{}, { url: '' }], name: '' }
            }
        };
        return _this2;
    }

    _createClass(SongInfo, [{
        key: "componentDidMount",
        value: function componentDidMount() {
            var _this3 = this;

            // Get track object from Spotify API
            var trackId = this.state.uri.match(/spotify\:track\:([a-zA-Z0-9]{22})/)[1];
            axios.get('https://api.spotify.com/v1/tracks/' + trackId).then(function (res) {
                _this3.setState({ track: res.data });
            });
        }
    }, {
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { className: "col-md-8 songInfo" },
                React.createElement("img", { src: this.state.track.album.images[1].url, className: "img img-rounded" }),
                React.createElement(
                    "div",
                    { className: "textInfo" },
                    React.createElement(
                        "span",
                        { className: "trackName" },
                        this.state.track.name
                    ),
                    React.createElement(
                        "span",
                        { className: "trackArtist" },
                        "By ",
                        this.state.track.artists[0].name
                    ),
                    React.createElement(
                        "span",
                        { className: "trackAlbum" },
                        this.state.track.album.name
                    )
                )
            );
        }
    }]);

    return SongInfo;
}(React.Component);

var Song = function (_React$Component3) {
    _inherits(Song, _React$Component3);

    function Song() {
        _classCallCheck(this, Song);

        return _possibleConstructorReturn(this, (Song.__proto__ || Object.getPrototypeOf(Song)).apply(this, arguments));
    }

    _createClass(Song, [{
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { className: "song row" },
                React.createElement(SongInfo, { uri: this.props.uri }),
                React.createElement(VoteControl, { maxPoints: null, minPoints: null, uri: this.props.uri, onUpVote: this.props.onUpVote, onDownVote: this.props.onDownVote })
            );
        }
    }]);

    return Song;
}(React.Component);

var SongListHeader = function (_React$Component4) {
    _inherits(SongListHeader, _React$Component4);

    function SongListHeader() {
        _classCallCheck(this, SongListHeader);

        return _possibleConstructorReturn(this, (SongListHeader.__proto__ || Object.getPrototypeOf(SongListHeader)).apply(this, arguments));
    }

    _createClass(SongListHeader, [{
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { className: "songListHeader" },
                React.createElement(
                    "div",
                    { className: "container" },
                    React.createElement(
                        "div",
                        { className: "row" },
                        React.createElement(
                            "div",
                            { className: "hidden-xs col-sm-4 col-md-4 vcenter text-center" },
                            React.createElement(
                                "span",
                                null,
                                "Choose A Song And Add Points To Begin!"
                            )
                        ),
                        React.createElement(
                            "div",
                            { className: "col-xs-6 col-ms-3 col-md-4 vcenter text-center" },
                            React.createElement(
                                "div",
                                { className: "progressWrapper" },
                                React.createElement(
                                    "span",
                                    { className: "progressIndicator" },
                                    React.createElement(
                                        "span",
                                        { className: "numSpent" },
                                        this.props.upVotes > 9 ? "" + this.props.upVotes : "0" + this.props.upVotes
                                    ),
                                    " of ",
                                    React.createElement(
                                        "span",
                                        { className: "maxVotes" },
                                        this.props.maxUpVotes > 9 ? "" + this.props.maxUpVotes : "0" + this.props.maxUpVotes
                                    )
                                ),
                                React.createElement("span", { className: "statusIcon upVote" })
                            )
                        ),
                        React.createElement(
                            "div",
                            { className: this.props.enabled ? 'col-xs-6 col-sm-5 col-md-4 vcenter text-center' : 'col-xs-6 col-sm-5 col-md-4 vcenter text-center disabled', id: "submitVotesButtonWrapper" },
                            React.createElement(
                                "button",
                                { type: "submit", id: "submitVotesButton", className: this.props.enabled ? 'btn btn-lg' : 'btn btn-lg disabled', disabled: !this.props.enabled },
                                "Submit",
                                React.createElement(
                                    "span",
                                    { className: "hidden-xs" },
                                    " Votes"
                                ),
                                "!"
                            )
                        )
                    )
                )
            );
        }
    }]);

    return SongListHeader;
}(React.Component);

var SongListHeaderWithDownVotes = function (_React$Component5) {
    _inherits(SongListHeaderWithDownVotes, _React$Component5);

    function SongListHeaderWithDownVotes() {
        _classCallCheck(this, SongListHeaderWithDownVotes);

        return _possibleConstructorReturn(this, (SongListHeaderWithDownVotes.__proto__ || Object.getPrototypeOf(SongListHeaderWithDownVotes)).apply(this, arguments));
    }

    _createClass(SongListHeaderWithDownVotes, [{
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { className: "songListHeader" },
                React.createElement(
                    "div",
                    { className: "container" },
                    React.createElement(
                        "div",
                        { className: "row" },
                        React.createElement(
                            "div",
                            { className: "col-xs-6 col-ms-3 col-md-4 vcenter text-center" },
                            React.createElement(
                                "div",
                                { className: "progressWrapper" },
                                React.createElement(
                                    "span",
                                    { className: "progressIndicator" },
                                    React.createElement(
                                        "span",
                                        { className: "numSpent" },
                                        this.props.upVotes > 9 ? "" + this.props.upVotes : "0" + this.props.upVotes
                                    ),
                                    " of ",
                                    React.createElement(
                                        "span",
                                        { className: "maxVotes" },
                                        this.props.maxUpVotes > 9 ? "" + this.props.maxUpVotes : "0" + this.props.maxUpVotes
                                    )
                                ),
                                React.createElement("span", { className: "statusIcon upVote" })
                            )
                        ),
                        React.createElement(
                            "div",
                            { className: "col-xs-6 col-ms-3 col-md-4 vcenter text-center" },
                            React.createElement(
                                "div",
                                { className: "progressWrapper" },
                                React.createElement(
                                    "span",
                                    { className: "progressIndicator" },
                                    React.createElement(
                                        "span",
                                        { className: "numSpent" },
                                        this.props.downVotes > 9 ? "" + this.props.downVotes : "0" + this.props.downVotes
                                    ),
                                    " of ",
                                    React.createElement(
                                        "span",
                                        { className: "maxVotes" },
                                        this.props.maxDownVotes > 9 ? "" + this.props.maxDownVotes : "0" + this.props.maxDownVotes
                                    )
                                ),
                                React.createElement("span", { className: "statusIcon downVote" })
                            )
                        ),
                        React.createElement(
                            "div",
                            { className: this.props.enabled ? 'col-xs-6 col-sm-5 col-md-4 vcenter text-center' : 'col-xs-6 col-sm-5 col-md-4 vcenter text-center disabled', id: "submitVotesButtonWrapper" },
                            React.createElement(
                                "button",
                                { type: "submit", id: "submitVotesButton", className: this.props.enabled ? 'btn btn-lg' : 'btn btn-lg disabled', disabled: !this.props.enabled },
                                "Submit",
                                React.createElement(
                                    "span",
                                    { className: "hidden-xs" },
                                    " Votes"
                                ),
                                "!"
                            )
                        )
                    )
                )
            );
        }
    }]);

    return SongListHeaderWithDownVotes;
}(React.Component);

var SongList = function (_React$Component6) {
    _inherits(SongList, _React$Component6);

    function SongList(props) {
        _classCallCheck(this, SongList);

        var _this7 = _possibleConstructorReturn(this, (SongList.__proto__ || Object.getPrototypeOf(SongList)).call(this, props));

        _this7.state = {
            upVotes: 0,
            downVotes: 0,
            votes: {}
        };
        return _this7;
    }

    _createClass(SongList, [{
        key: "render",
        value: function render() {
            var listHeader = null;
            var headerEnabled = this.state.upVotes == this.props.maxUpVotes && (this.props.maxDownVotes == null || this.state.downVotes == this.props.maxDownVotes);

            if (this.props.maxDownVotes == null) {
                listHeader = React.createElement(SongListHeader, { upVotes: this.state.upVotes, maxUpVotes: this.props.maxUpVotes, enabled: headerEnabled });
            } else {
                listHeader = React.createElement(SongListHeaderWithDownVotes, { upVotes: this.state.upVotes, maxUpVotes: this.props.maxUpVotes, downVotes: this.state.downVotes, maxDownVotes: this.props.maxDownVotes, enabled: headerEnabled });
            }

            return React.createElement(
                "div",
                null,
                React.createElement(
                    "form",
                    { onSubmit: this.handleFormSubmission.bind(this) },
                    listHeader,
                    React.createElement(
                        "div",
                        { className: "songList" },
                        React.createElement(
                            "div",
                            { className: "container" },

                            // TODO: Pass min/max points allowed per song, null if not set
                            this.props.uris.map(function (uri) {
                                return React.createElement(Song, { uri: uri, onUpVote: this.onUpVote.bind(this), onDownVote: this.onDownVote.bind(this) });
                            }.bind(this))
                        )
                    )
                )
            );
        }
    }, {
        key: "handleFormSubmission",
        value: function handleFormSubmission() {
            console.log("Form submitted: " + JSON.stringify(this.state.votes));
            return false;
        }
    }, {
        key: "onUpVote",
        value: function onUpVote(uri, newPointValue) {
            /* When a song in the SongList is upvoted, we need to determine
            whether the user is removing a downvote or adding an upvote. If
            the user is adding an upvote, we need to reject the upvote when
            it exceeds the allowance.
            */
            if (newPointValue <= 0) {
                console.log("Song vote " + newPointValue + " is still negative. Will allow.");
                var newVotesState = this.state.votes;
                newVotesState[uri] = newPointValue;
                this.setState({ downVotes: this.state.downVotes - 1, votes: newVotesState });
            } else {
                var newUpVotesValue = this.state.upVotes + 1;

                if (newUpVotesValue <= this.props.maxUpVotes) {
                    console.log("Up vote count " + newUpVotesValue + " within allowance. Will allow.");
                    var newVotesState = this.state.votes;
                    newVotesState[uri] = newPointValue;
                    this.setState({ upVotes: this.state.upVotes + 1, votes: newVotesState });
                } else {
                    console.log("Up vote count " + newUpVotesValue + " exceeds total allowance. Rejecting.");
                    return false;
                }
            }

            return true;
        }
    }, {
        key: "onDownVote",
        value: function onDownVote(uri, newPointValue) {
            /* When a song in the SongList is downvoted, we need to determine
            whether the user is removing an upvote or adding a downvote. If
            the user is adding a downvote, we need to reject the downvote When
            it exceeds the allowance.
            */
            if (newPointValue >= 0) {
                console.log("Song vote " + newPointValue + " is still positive. Will allow.");
                var newVotesState = this.state.votes;
                newVotesState[uri] = newPointValue;
                this.setState({ upVotes: this.state.upVotes - 1, votes: newVotesState });
            } else {
                var newDownVotesValue = this.state.downVotes + 1;

                if (newDownVotesValue <= this.props.maxDownVotes) {
                    console.log("Down vote count " + newDownVotesValue + " within allowance. Will allow.");
                    var newVotesState = this.state.votes;
                    newVotesState[uri] = newPointValue;
                    this.setState({ downVotes: this.state.downVotes + 1, votes: newVotesState });
                } else {
                    console.log("Down vote count " + newDownVotesValue + " exceeds total allowance. Rejecting.");
                    return false;
                }
            }

            return true;
        }
    }]);

    return SongList;
}(React.Component);

/*
NOTE: Currently rendered on template in order to inject data prior to page load
ReactDOM.render(
    <SongList
        uris={["spotify:track:429EttO8gs0bDo2SQfUNSm", "spotify:track:5Ykzu4eg5UEVJP3LCoxgpF", "spotify:track:6DXFVsLcEvOTSrkG9G1Cb1", "spotify:track:6GyFP1nfCDB8lbD2bG0Hq9", "spotify:track:0x4rW5jv6fkKweBgjE5O8F"]}
        maxDownVotes={0} maxUpVotes={10}/>,
    document.getElementById('mountVote')
);
*/