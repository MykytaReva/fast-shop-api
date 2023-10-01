import React, {Component} from "react";

class PostDetail extends Component {
    constructor(props) {
        super(props)
        this.titleWasClicked = this.titleWasClicked.bind(this)
    }
    titleWasClicked = (event) => {
        event.preventDefault();
        alert(this.props)
        console.log(this.props)
    }
    render() {
        const {post} = this.props;
        return (
            <div>
                <h3 onClick={this.titleWasClicked}>{post.title}</h3>
                <p>{post.content}</p>
            </div>
        )
    }
}
export default PostDetail;