module Main exposing (main)

import Browser
import Element exposing (..)
import Element.Input as Input
import Html
import Http
import Json.Decode as JD
import Json.Encode as JE



-- INIT


init : () -> ( Model, Cmd Msg )
init _ =
    ( initialModel, Cmd.none )



-- MODEL


type alias Model =
    { input : String
    , output : String
    , error : String
    }


initialModel : Model
initialModel =
    { input = ""
    , output = ""
    , error = ""
    }



-- UPDATE


type Msg
    = ChangedInput String
    | SendData
    | ReceivedData (Result Http.Error String)


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangedInput input ->
            ( { model | input = input }
            , Cmd.none
            )

        SendData ->
            ( model
            , sendData model.input
            )

        ReceivedData result ->
            case result of
                Ok output ->
                    ( { model | output = output }
                    , Cmd.none
                    )

                Err error ->
                    ( { model | error = decodeError error }
                    , Cmd.none
                    )


sendData : String -> Cmd Msg
sendData input =
    Http.post
        { url = "/api/user"
        , body = Http.jsonBody (inputEncoder input)
        , expect = Http.expectJson ReceivedData outputDecoder
        }



-- ENCODER


inputEncoder : String -> JE.Value
inputEncoder input =
    JE.object [ ( "input", JE.string input ) ]



-- DECODERS


outputDecoder : JD.Decoder String
outputDecoder =
    JD.field "output" JD.string


decodeError : Http.Error -> String
decodeError error =
    case error of
        Http.BadUrl err ->
            err

        Http.Timeout ->
            "Timeout"

        Http.NetworkError ->
            "Network Error"

        Http.BadStatus status ->
            "Error " ++ String.fromInt status

        Http.BadBody err ->
            err



-- VIEW


view : Model -> Html.Html Msg
view model =
    layout
        [ height fill
        , width fill
        ]
        (column
            [ centerX
            , centerY
            , spacing 20
            ]
            [ row
                [ spacing 20 ]
                [ Input.text
                    []
                    { onChange = ChangedInput
                    , text = model.input
                    , label =
                        Input.labelHidden
                            "Input"
                    , placeholder =
                        Just <|
                            Input.placeholder
                                []
                                (text "User ID")
                    }
                , Input.button
                    []
                    { label = text "Click"
                    , onPress = Just SendData
                    }
                ]
            , text "Recommendation"
            , newTabLink []
                { url = model.output
                , label = text model.output
                }
            , text model.error
            ]
        )



-- MAIN


main : Program () Model Msg
main =
    Browser.element
        { init = init
        , view = view
        , update = update
        , subscriptions = \_ -> Sub.none
        }