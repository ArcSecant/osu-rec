module PP exposing (..)

import Browser
import Element exposing (..)
import Element.Input as Input
import Element.Background as Background
import Element.Border as Border
import Element.Font as Font
import Html
import Http
import Json.Decode as JD
import Json.Encode as JE



-- INIT


init : () -> ( Model, Cmd Msg )
init _ =
    ( initialModel, Cmd.none )



-- MODEL

type alias Output = 
    { url : String
    , mods : String
    }

type alias Model =
    { input : String
    , output : Output
    , error : String
    }


initialModel : Model
initialModel =
    { input = ""
    , output = 
        { url = ""
        , mods = ""
        }
    , error = ""
    }

clickableAttributes : List (Attribute msg)
clickableAttributes =
    [ padding 12
    , Border.width 1
    , Border.rounded 3
    , Border.color <| rgb255 0xC0 0xC0 0xC0
    , Font.color <| rgb255 0x00 0x00 0x00
    ]


-- UPDATE


type Msg
    = ChangedInput String
    | SendData
    | ReceivedData (Result Http.Error Output)


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
        { url = "/api/pp"
        , body = Http.jsonBody (inputEncoder input)
        , expect = Http.expectJson ReceivedData outputDecoder
        }



-- ENCODER


inputEncoder : String -> JE.Value
inputEncoder input =
    JE.object [ ( "input", JE.string input ) ]



-- DECODERS


outputDecoder : JD.Decoder Output
outputDecoder =
    JD.map2 Output
        (JD.field "url" JD.string)
        (JD.field "mods" JD.string)


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
            [ column
                [ spacing 20
                , centerX ]
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
                        clickableAttributes
                        { label = text "Click"
                        , onPress = Just SendData
                        }
                    ]
                , text "Recommendation"
                , newTabLink []
                    { url = model.output.url
                    , label = text model.output.url
                    }
                , text model.output.mods
                , text model.error
                ]
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